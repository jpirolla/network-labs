"""
service-a/main.py
-----------------
Serviço de processamento de pedidos.

Responsável por:
  1. Receber o pedido do API Gateway (com trace context propagado)
  2. Processar os itens do pedido (lógica de negócio simulada)
  3. Chamar Service B para enriquecimento externo
  4. Enfileirar uma tarefa no Redis para o Worker processar assincronamente

CONCEITO: Trace Propagation (Propagação de Contexto)
  Quando o API Gateway chama este serviço, ele envia o header:
    traceparent: 00-{trace_id}-{parent_span_id}-01
  
  O extract() do OTel lê esse header e "continua" o trace original.
  Isso significa que todos os spans criados aqui serão filhos do span
  do Gateway, formando uma árvore de spans rastreável no Jaeger.
"""

import asyncio
import json
import os
import random
import time
from contextlib import asynccontextmanager

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, Request
from opentelemetry import trace, propagate, context
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.propagate import extract, inject
from opentelemetry.trace import SpanKind, Status, StatusCode

import sys
sys.path.insert(0, "/app/shared")
from telemetry import setup_telemetry, setup_logging

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

SERVICE_NAME = "service-a"
SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://service-b:8002")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

tracer, meter = setup_telemetry(SERVICE_NAME)
logger = setup_logging(SERVICE_NAME)

# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

processed_orders = meter.create_counter(
    "service_a_orders_processed_total",
    description="Total de pedidos processados pelo Service A",
)

processing_time = meter.create_histogram(
    "service_a_processing_duration_seconds",
    description="Tempo de processamento no Service A",
    unit="s",
)

items_processed = meter.create_histogram(
    "service_a_items_per_order",
    description="Distribuição de itens por pedido",
    unit="1",
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

redis_client: aioredis.Redis | None = None
http_client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, http_client
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    http_client = httpx.AsyncClient(timeout=8.0)
    logger.info("Service A iniciando — Redis e HTTP client prontos")
    yield
    await redis_client.aclose()
    await http_client.aclose()
    logger.info("Service A encerrando")


app = FastAPI(title="Service A — Order Processor", version="1.0.0", lifespan=lifespan)
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": SERVICE_NAME}


@app.post("/process")
async def process_order(order: dict, request: Request):
    """
    Processa um pedido: valida itens, chama Service B e enfileira no worker.

    CONCEITO: extract() — extraindo contexto propagado
      O FastAPIInstrumentor já faz extract() automaticamente e cria o span
      raiz para este endpoint. Mas se precisarmos fazer manualmente:
        ctx = extract(dict(request.headers))
        with tracer.start_as_current_span("...", context=ctx): ...
    """
    start = time.perf_counter()
    order_id = order.get("order_id", "unknown")
    items = order.get("items", [])
    priority = order.get("priority", "normal")

    logger.info(f"Processando pedido order_id={order_id} items={items}")

    # O span desta função já existe (criado pelo FastAPIInstrumentor)
    current_span = trace.get_current_span()
    current_span.set_attribute("order.id", order_id)
    current_span.set_attribute("order.priority", priority)
    current_span.set_attribute("order.items_count", len(items))

    try:
        # --- Span: Processamento de Itens ---
        result_items = []
        with tracer.start_as_current_span(
            "process_order_items",
            kind=SpanKind.INTERNAL,
            attributes={"items.count": len(items)},
        ) as proc_span:
            for item in items:
                # Simula processamento por item: 10–50ms
                processing_delay = random.uniform(0.01, 0.05)
                await asyncio.sleep(processing_delay)
                result_items.append({
                    "item_id": item,
                    "status": "validated",
                    "processing_ms": round(processing_delay * 1000, 1),
                })
                proc_span.add_event(
                    "item_processed",
                    attributes={"item.id": item, "delay_ms": processing_delay * 1000},
                )
            
            proc_span.set_attribute("items.processed", len(result_items))

        items_processed.record(len(items), {"priority": priority})

        # --- Span: Chamada ao Service B (enriquecimento externo) ---
        enrichment_data = None
        with tracer.start_as_current_span(
            "call_service_b_enrichment",
            kind=SpanKind.CLIENT,
        ) as b_span:
            headers = {}
            inject(headers)  # propaga o trace atual

            try:
                b_response = await http_client.post(
                    f"{SERVICE_B_URL}/enrich",
                    json={"order_id": order_id, "items_count": len(items)},
                    headers=headers,
                )
                b_span.set_attribute("http.status_code", b_response.status_code)

                if b_response.status_code == 200:
                    enrichment_data = b_response.json()
                    b_span.set_attribute("enrichment.success", True)
                else:
                    # Service B retornou erro — degradamos gracefully
                    b_span.set_attribute("enrichment.success", False)
                    b_span.set_attribute("enrichment.fallback", True)
                    b_span.set_status(Status(StatusCode.ERROR, f"Service B: {b_response.status_code}"))
                    enrichment_data = {"status": "enrichment_unavailable", "fallback": True}
                    logger.warning(f"Service B retornou {b_response.status_code} para order_id={order_id}")

            except httpx.TimeoutException:
                b_span.set_status(Status(StatusCode.ERROR, "timeout"))
                enrichment_data = {"status": "timeout", "fallback": True}
                logger.warning(f"Timeout ao chamar Service B para order_id={order_id}")

        # --- Span: Enfileirar no Redis para o Worker ---
        with tracer.start_as_current_span(
            "enqueue_worker_task",
            kind=SpanKind.PRODUCER,  # SpanKind.PRODUCER = publicador de mensagem
        ) as enqueue_span:
            # CONCEITO: Propagação via fila (async trace propagation)
            # O W3C TraceContext é serializado como string e enviado junto com
            # a mensagem. O Worker deserializa e continua o trace.
            carrier: dict = {}
            inject(carrier)  # captura traceparent e tracestate

            task_payload = json.dumps({
                "order_id": order_id,
                "items": items,
                "priority": priority,
                "otel_context": carrier,  # trace context serializado
            })

            await redis_client.rpush("worker:tasks", task_payload)
            enqueue_span.set_attribute("messaging.system", "redis")
            enqueue_span.set_attribute("messaging.destination", "worker:tasks")
            enqueue_span.set_attribute("order.id", order_id)

            logger.info(f"Tarefa enfileirada para worker order_id={order_id}")

        # Métricas finais
        elapsed = time.perf_counter() - start
        processing_time.record(elapsed, {"priority": priority, "status": "success"})
        processed_orders.add(1, {"priority": priority, "status": "success"})

        return {
            "order_id": order_id,
            "status": "processed",
            "items_result": result_items,
            "enrichment": enrichment_data,
            "processing_ms": round(elapsed * 1000, 2),
        }

    except Exception as e:
        elapsed = time.perf_counter() - start
        processing_time.record(elapsed, {"priority": priority, "status": "error"})
        processed_orders.add(1, {"priority": priority, "status": "error"})
        current_span.record_exception(e)
        current_span.set_status(Status(StatusCode.ERROR, str(e)))
        logger.error(f"Erro processando order_id={order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
