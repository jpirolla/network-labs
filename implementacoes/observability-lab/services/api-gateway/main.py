"""
api-gateway/main.py
-------------------
Ponto de entrada da arquitetura. Recebe requisições do cliente,
valida, e orquestra chamadas para o Service A.

CONCEITO: API Gateway no contexto de Observabilidade
  O Gateway é onde o trace "nasce". Ele cria o root span e propaga
  o contexto para todos os serviços downstream via headers HTTP.
  Sem propagação, cada serviço teria seu próprio trace isolado,
  sendo impossível ver a jornada completa da requisição.
"""

import random
import time
import asyncio
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.propagate import inject
from opentelemetry.trace import SpanKind, Status, StatusCode

import sys
sys.path.insert(0, "/app/shared")
from telemetry import setup_telemetry, setup_logging

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

SERVICE_NAME = "api-gateway"
SERVICE_A_URL = os.getenv("SERVICE_A_URL", "http://service-a:8001")

# Inicializa OTel (tracer + meter) e logging estruturado
tracer, meter = setup_telemetry(SERVICE_NAME)
logger = setup_logging(SERVICE_NAME)

# ---------------------------------------------------------------------------
# Métricas customizadas
# CONCEITO: Instrumentação Manual de Métricas
#   A instrumentação automática captura latência HTTP básica, mas não sabe
#   nada sobre a semântica do negócio. Aqui criamos métricas que expressam
#   o significado do domínio: quantos pedidos foram processados, com que
#   latência, e com que taxa de erro.
# ---------------------------------------------------------------------------

# Counter: acumula total de requisições, com labels para filtrar no Grafana
requests_counter = meter.create_counter(
    name="gateway_requests_total",
    description="Total de requisições recebidas pelo API Gateway",
    unit="1",
)

# Histogram: distribui latências em buckets (p50, p90, p99)
latency_histogram = meter.create_histogram(
    name="gateway_request_duration_seconds",
    description="Latência das requisições no API Gateway",
    unit="s",
)

# UpDownCounter: rastreia requisições em andamento (gauge-like)
in_flight_gauge = meter.create_up_down_counter(
    name="gateway_requests_in_flight",
    description="Requisições em andamento no API Gateway",
    unit="1",
)

# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

class OrderRequest(BaseModel):
    order_id: str
    items: list[str]
    priority: str = "normal"  # normal | high

class OrderResponse(BaseModel):
    order_id: str
    status: str
    trace_id: str
    processing_time_ms: float
    service_a_response: dict | None = None

# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Gateway iniciando...")
    yield
    logger.info("API Gateway encerrando...")

app = FastAPI(
    title="API Gateway — Observability Lab",
    description="Ponto de entrada da arquitetura de microserviços instrumentada com OpenTelemetry",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Instrumentação Automática do FastAPI e HTTPX
# CONCEITO: Instrumentação Automática
#   O FastAPIInstrumentor "envolve" automaticamente todos os endpoints,
#   criando spans para cada requisição HTTP recebida sem precisar de código
#   extra nos handlers. Da mesma forma, HTTPXClientInstrumentor intercepta
#   chamadas de saída e injeta os headers de propagação automaticamente.
#
# LIMITAÇÃO: A auto-instrumentação não conhece a semântica do negócio.
#   Ela cria spans genéricos como "POST /order". Para enriquecer com
#   atributos de negócio (order_id, priority, etc.), usamos spans manuais.
# ---------------------------------------------------------------------------

FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()

# ---------------------------------------------------------------------------
# HTTP Client compartilhado (reutiliza conexões)
# ---------------------------------------------------------------------------

http_client = httpx.AsyncClient(timeout=10.0)

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Health check para o Docker Compose e load balancers."""
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/metrics-info")
async def metrics_info():
    """Endpoint informativo sobre métricas disponíveis (não é o /metrics do Prometheus)."""
    return {
        "note": "Métricas Prometheus disponíveis via OTel Collector na porta 9090",
        "metrics": [
            "gateway_requests_total",
            "gateway_request_duration_seconds",
            "gateway_requests_in_flight",
        ],
    }


@app.post("/order", response_model=OrderResponse)
async def create_order(order: OrderRequest, request: Request):
    """
    Endpoint principal: processa um pedido através dos microserviços.
    
    Fluxo:
      1. Valida a requisição (span manual: validate_request)
      2. Chama Service A para processar o pedido
      3. Retorna resposta consolidada com trace_id
    """
    start_time = time.perf_counter()
    
    # Labels para métricas (aparecem no Grafana como dimensões filtráreis)
    metric_labels = {
        "endpoint": "/order",
        "method": "POST",
        "priority": order.priority,
    }
    
    in_flight_gauge.add(1, metric_labels)
    requests_counter.add(1, metric_labels)
    
    # Captura o span pai criado pela auto-instrumentação do FastAPI
    current_span = trace.get_current_span()
    ctx = current_span.get_span_context()
    trace_id_hex = format(ctx.trace_id, "032x") if ctx.is_valid else "unknown"
    
    logger.info(
        f"Recebido pedido order_id={order.order_id} priority={order.priority} items={len(order.items)}"
    )
    
    try:
        # --- Span Manual: Validação ---
        # CONCEITO: Span Manual
        #   Aqui criamos um span filho explicitamente para medir apenas
        #   a etapa de validação. No Jaeger, isso aparece como sub-span
        #   do span raiz, permitindo identificar onde o tempo é gasto.
        with tracer.start_as_current_span(
            "validate_request",
            kind=SpanKind.INTERNAL,
            attributes={
                "order.id": order.order_id,
                "order.items_count": len(order.items),
                "order.priority": order.priority,
            },
        ) as validation_span:
            
            # Validação: pedidos de alta prioridade precisam de pelo menos 1 item
            if not order.items:
                validation_span.set_status(Status(StatusCode.ERROR, "Pedido vazio"))
                validation_span.set_attribute("validation.passed", False)
                raise HTTPException(status_code=422, detail="O pedido deve conter ao menos 1 item")
            
            # Simula lógica de validação: ~5ms
            await asyncio.sleep(0.005)
            validation_span.set_attribute("validation.passed", True)
        
        # --- Chamada para Service A ---
        # CONCEITO: Propagação de Contexto
        #   O HTTPXClientInstrumentor já injeta o header 'traceparent' 
        #   automaticamente nas chamadas httpx. Mas também podemos fazer
        #   manualmente com inject() para ter controle explícito.
        #   
        #   O header 'traceparent' tem o formato:
        #   00-{trace_id}-{span_id}-{flags}
        #   Exemplo: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
        
        with tracer.start_as_current_span(
            "call_service_a",
            kind=SpanKind.CLIENT,
            attributes={
                "http.url": f"{SERVICE_A_URL}/process",
                "order.id": order.order_id,
            },
        ) as client_span:
            
            headers = {}
            inject(headers)  # Injeta traceparent + tracestate nos headers
            
            try:
                response = await http_client.post(
                    f"{SERVICE_A_URL}/process",
                    json=order.model_dump(),
                    headers=headers,
                )
                
                client_span.set_attribute("http.status_code", response.status_code)
                
                if response.status_code >= 500:
                    client_span.set_status(
                        Status(StatusCode.ERROR, f"Service A retornou {response.status_code}")
                    )
                    raise HTTPException(
                        status_code=502,
                        detail=f"Service A falhou: {response.text}",
                    )
                
                service_a_data = response.json()
                
            except httpx.TimeoutException as e:
                client_span.set_status(Status(StatusCode.ERROR, "Timeout"))
                client_span.record_exception(e)
                logger.error(f"Timeout chamando Service A para order_id={order.order_id}")
                raise HTTPException(status_code=504, detail="Service A timeout")
        
        # Registra sucesso no span pai
        current_span.set_attribute("order.id", order.order_id)
        current_span.set_attribute("order.status", "completed")
        
        elapsed = (time.perf_counter() - start_time) * 1000  # ms
        latency_histogram.record(elapsed / 1000, {**metric_labels, "status": "success"})
        
        logger.info(
            f"Pedido concluído order_id={order.order_id} latency_ms={elapsed:.2f}"
        )
        
        return OrderResponse(
            order_id=order.order_id,
            status="completed",
            trace_id=trace_id_hex,
            processing_time_ms=round(elapsed, 2),
            service_a_response=service_a_data,
        )
    
    except HTTPException:
        elapsed = (time.perf_counter() - start_time) * 1000
        latency_histogram.record(elapsed / 1000, {**metric_labels, "status": "error"})
        current_span.set_attribute("order.status", "failed")
        raise
    
    except Exception as e:
        elapsed = (time.perf_counter() - start_time) * 1000
        latency_histogram.record(elapsed / 1000, {**metric_labels, "status": "error"})
        current_span.record_exception(e)
        current_span.set_status(Status(StatusCode.ERROR, str(e)))
        logger.error(f"Erro inesperado order_id={order.order_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")
    
    finally:
        in_flight_gauge.add(-1, metric_labels)


@app.post("/order/batch")
async def create_order_batch(orders: list[OrderRequest]):
    """
    Processa múltiplos pedidos em paralelo.
    Demonstra como múltiplos traces coexistem e como o Grafana
    mostra throughput agregado.
    """
    tasks = [create_order.__wrapped__(order, None) if hasattr(create_order, '__wrapped__') else None for order in orders]
    
    results = []
    for order in orders:
        try:
            # Chama sequencialmente para manter clareza didática
            result = await http_client.post(
                f"http://localhost:8000/order",
                json=order.model_dump(),
            )
            results.append(result.json())
        except Exception as e:
            results.append({"order_id": order.order_id, "status": "error", "detail": str(e)})
    
    return {"processed": len(results), "results": results}
