"""
service-b/main.py
-----------------
Simulador de serviço externo com comportamento caótico proposital.

Este serviço existe para demonstrar:
  1. Latência variável (100ms–2s) — simula APIs reais lentas
  2. Erros intermitentes (20%) — simula instabilidade
  3. Timeouts ocasionais (10%) — simula sobrecarga ou rede ruim
  4. Como spans marcam erros e como o Jaeger exibe traces falhos

CONCEITO: Por que simular falhas é importante para SRE?
  Em produção, sistemas falham o tempo todo. Um sistema observável
  deve ser capaz de:
    - Detectar falhas rapidamente (alertas no Grafana)
    - Localizar a causa raiz (trace no Jaeger)
    - Quantificar o impacto (métricas de error rate no Prometheus)
  
  Este serviço gera o "ruído" que torna os dashboards interessantes.
"""

import asyncio
import os
import random
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import SpanKind, Status, StatusCode

import sys
sys.path.insert(0, "/app/shared")
from telemetry import setup_telemetry, setup_logging

# ---------------------------------------------------------------------------
# Configuração de Caos (ajustável via env vars)
# ---------------------------------------------------------------------------

SERVICE_NAME = "service-b"

# Probabilidades de comportamento anômalo
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.20"))       # 20% de erros 503
TIMEOUT_RATE = float(os.getenv("TIMEOUT_RATE", "0.10"))   # 10% de timeouts (5s)
MIN_LATENCY_MS = float(os.getenv("MIN_LATENCY_MS", "100"))
MAX_LATENCY_MS = float(os.getenv("MAX_LATENCY_MS", "2000"))
TIMEOUT_SLEEP_MS = float(os.getenv("TIMEOUT_SLEEP_MS", "5000"))

tracer, meter = setup_telemetry(SERVICE_NAME)
logger = setup_logging(SERVICE_NAME)

# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

enrichment_requests = meter.create_counter(
    "service_b_requests_total",
    description="Total de requisições recebidas pelo Service B",
)

enrichment_latency = meter.create_histogram(
    "service_b_latency_seconds",
    description="Latência simulada do Service B",
    unit="s",
)

error_counter = meter.create_counter(
    "service_b_errors_total",
    description="Total de erros simulados pelo Service B",
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"Service B iniciando — error_rate={ERROR_RATE:.0%} "
        f"timeout_rate={TIMEOUT_RATE:.0%} "
        f"latency={MIN_LATENCY_MS:.0f}–{MAX_LATENCY_MS:.0f}ms"
    )
    yield
    logger.info("Service B encerrando")


app = FastAPI(
    title="Service B — External Simulator",
    description="Simula um serviço externo com latência variável e falhas intermitentes",
    version="1.0.0",
    lifespan=lifespan,
)
FastAPIInstrumentor.instrument_app(app)


# ---------------------------------------------------------------------------
# Lógica de Caos
# ---------------------------------------------------------------------------

def should_fail() -> bool:
    """20% de chance de retornar erro 503."""
    return random.random() < ERROR_RATE


def should_timeout() -> bool:
    """10% de chance de simular timeout."""
    return random.random() < TIMEOUT_RATE


def random_latency_ms() -> float:
    """Latência aleatória em distribuição não-uniforme (realista)."""
    # Mistura de distribuição normal (maioria rápida) + cauda longa
    base = random.uniform(MIN_LATENCY_MS, MAX_LATENCY_MS)
    # 5% de chance de latência na cauda (p95+ simulado)
    if random.random() < 0.05:
        return random.uniform(MAX_LATENCY_MS * 0.8, MAX_LATENCY_MS)
    return base


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": SERVICE_NAME}


@app.post("/enrich")
async def enrich_order(payload: dict, request: Request):
    """
    Enriquece dados de um pedido com informações externas (simuladas).
    
    Comportamento:
      - Latência aleatória: 100ms–2000ms
      - 20%: retorna erro 503 (service unavailable)
      - 10%: dorme 5s (provoca timeout no chamador)
      - 70%: retorna dados enriquecidos com sucesso
    
    CONCEITO: Como spans refletem falhas?
      Quando um erro ocorre, o span é marcado com:
        - span.set_status(Status(StatusCode.ERROR, ...))
        - span.record_exception(e)  — inclui stack trace
        - span.set_attribute("error", True)
      
      No Jaeger, spans com erro aparecem em vermelho.
      No Grafana, podemos filtrar por traces com erros usando:
        {status="error"}
    """
    order_id = payload.get("order_id", "unknown")
    
    # O span pai já foi criado pelo FastAPIInstrumentor
    current_span = trace.get_current_span()
    current_span.set_attribute("order.id", order_id)

    enrichment_requests.add(1, {"order_id_prefix": order_id[:4] if len(order_id) >= 4 else order_id})

    # --- Simulação de Timeout ---
    if should_timeout():
        timeout_ms = TIMEOUT_SLEEP_MS
        
        current_span.set_attribute("simulation.type", "timeout")
        current_span.set_attribute("simulation.sleep_ms", timeout_ms)
        current_span.set_status(Status(StatusCode.ERROR, "Simulated timeout"))
        
        logger.warning(
            f"Simulando timeout de {timeout_ms}ms para order_id={order_id}"
        )
        error_counter.add(1, {"type": "timeout"})
        
        # Dorme mais que o timeout do chamador (configurado para 8s no Service A)
        await asyncio.sleep(timeout_ms / 1000)
        
        # Se chegou aqui, o chamador pode ter desistido mas nós "respondemos"
        return JSONResponse(
            status_code=503,
            content={"error": "service_overloaded", "order_id": order_id},
        )

    # --- Latência Normal ---
    latency_ms = random_latency_ms()
    
    with tracer.start_as_current_span(
        "external_data_fetch",
        kind=SpanKind.INTERNAL,
        attributes={
            "simulation.latency_ms": latency_ms,
            "order.id": order_id,
        },
    ) as fetch_span:
        
        logger.info(f"Buscando dados externos para order_id={order_id} latency_ms={latency_ms:.1f}")
        await asyncio.sleep(latency_ms / 1000)
        
        # --- Simulação de Erro Intermitente ---
        if should_fail():
            fetch_span.set_attribute("simulation.type", "intermittent_error")
            fetch_span.set_status(
                Status(StatusCode.ERROR, "Simulated 503 — service temporarily unavailable")
            )
            error_counter.add(1, {"type": "intermittent_503"})
            enrichment_latency.record(latency_ms / 1000, {"outcome": "error"})
            
            logger.warning(f"Simulando erro 503 para order_id={order_id}")
            
            return JSONResponse(
                status_code=503,
                content={
                    "error": "service_temporarily_unavailable",
                    "retry_after": 2,
                    "order_id": order_id,
                    "trace_note": "Este erro foi simulado — veja o span 'external_data_fetch'",
                },
            )
        
        # --- Sucesso ---
        fetch_span.set_attribute("simulation.type", "success")
        fetch_span.add_event(
            "external_data_fetched",
            attributes={
                "provider": "mock_enrichment_api",
                "latency_ms": latency_ms,
            },
        )
        enrichment_latency.record(latency_ms / 1000, {"outcome": "success"})
        
        # Dados enriquecidos simulados
        enriched = {
            "order_id": order_id,
            "customer_segment": random.choice(["premium", "standard", "basic"]),
            "shipping_estimate_days": random.randint(1, 7),
            "fraud_score": round(random.uniform(0.0, 0.3), 3),  # baixo = seguro
            "enrichment_latency_ms": round(latency_ms, 1),
            "provider": "mock_external_api_v2",
            "simulation": {
                "actual_latency_ms": round(latency_ms, 1),
                "error_rate_config": ERROR_RATE,
                "timeout_rate_config": TIMEOUT_RATE,
            },
        }
        
        logger.info(
            f"Enriquecimento concluído order_id={order_id} "
            f"latency_ms={latency_ms:.1f} segment={enriched['customer_segment']}"
        )
        
        return enriched
