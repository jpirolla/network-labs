"""
worker/worker.py
----------------
Worker assíncrono que consome tarefas da fila Redis.

Demonstra o conceito mais avançado de observabilidade:
  Propagação de trace context através de uma fila assíncrona.

CONCEITO: Async Trace Propagation
  Quando o Service A enfileira uma tarefa, o trace já terminou do ponto
  de vista HTTP (o gateway respondeu ao cliente). Mas o processamento
  continua no worker.
  
  Para conectar os dois mundos, o Service A serializa o trace context
  (traceparent header) junto com a mensagem. O Worker deserializa e
  cria um span VINCULADO ao trace original.
  
  Resultado no Jaeger: o trace mostra spans do gateway, service-a,
  service-b, E do worker — mesmo que o worker tenha executado depois
  que o HTTP já respondeu.

SpanKind.CONSUMER:
  Indica que este span está "consumindo" uma mensagem de uma fila.
  O par PRODUCER (Service A) + CONSUMER (Worker) é uma convenção OTel
  para sistemas de mensageria.
"""

import asyncio
import json
import os
import random
import sys
import time

import redis.asyncio as aioredis
from opentelemetry import trace, propagate, context
from opentelemetry.propagate import extract
from opentelemetry.trace import SpanKind, Status, StatusCode, Link

sys.path.insert(0, "/app/shared")
from telemetry import setup_telemetry, setup_logging

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

SERVICE_NAME = "worker"
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
QUEUE_KEY = "worker:tasks"
WORKER_ID = os.getenv("WORKER_ID", "worker-1")

tracer, meter = setup_telemetry(SERVICE_NAME)
logger = setup_logging(SERVICE_NAME)

# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

tasks_processed = meter.create_counter(
    "worker_tasks_processed_total",
    description="Total de tarefas processadas pelo worker",
)

task_duration = meter.create_histogram(
    "worker_task_duration_seconds",
    description="Tempo de processamento por tarefa no worker",
    unit="s",
)

queue_depth_gauge = meter.create_up_down_counter(
    "worker_queue_depth",
    description="Profundidade estimada da fila de tarefas",
)

# ---------------------------------------------------------------------------
# Lógica de Processamento
# ---------------------------------------------------------------------------

async def process_task(task_data: dict) -> dict:
    """
    Processa uma tarefa retirada da fila.
    
    CONCEITO: Recuperando o trace context da fila
      A tarefa contém {"otel_context": {"traceparent": "00-abc...-def...-01"}}
      Usamos extract() para recuperar o SpanContext original e criamos
      um span ligado a ele.
    """
    order_id = task_data.get("order_id", "unknown")
    items = task_data.get("items", [])
    priority = task_data.get("priority", "normal")
    otel_ctx_carrier = task_data.get("otel_context", {})

    # Recupera o contexto propagado (SpanContext do Service A)
    remote_ctx = extract(otel_ctx_carrier)
    remote_span_ctx = (
        trace.get_current_span(remote_ctx).get_span_context()
        if remote_ctx
        else None
    )

    # Cria links para o span original (melhor prática para filas)
    # Link = "este span está relacionado a" (diferente de filho direto)
    links = []
    if remote_span_ctx and remote_span_ctx.is_valid:
        links.append(Link(remote_span_ctx))

    start = time.perf_counter()

    with tracer.start_as_current_span(
        "worker.process_task",
        kind=SpanKind.CONSUMER,
        context=remote_ctx,  # Continua sob o mesmo trace
        links=links,
        attributes={
            "order.id": order_id,
            "order.items_count": len(items),
            "order.priority": priority,
            "messaging.system": "redis",
            "messaging.destination": QUEUE_KEY,
            "worker.id": WORKER_ID,
        },
    ) as task_span:

        logger.info(f"Worker iniciando processamento order_id={order_id} items={items}")

        # --- Etapa 1: Enriquecimento de dados ---
        with tracer.start_as_current_span(
            "worker.enrich_data",
            kind=SpanKind.INTERNAL,
        ) as enrich_span:
            enrich_delay = random.uniform(0.1, 0.4)
            await asyncio.sleep(enrich_delay)
            enrich_span.set_attribute("enrichment.delay_ms", enrich_delay * 1000)
            enrich_span.add_event("data_enriched", {"source": "internal_cache"})

        # --- Etapa 2: Persistência (simulada) ---
        with tracer.start_as_current_span(
            "worker.persist_to_db",
            kind=SpanKind.INTERNAL,
        ) as persist_span:
            persist_delay = random.uniform(0.05, 0.3)
            await asyncio.sleep(persist_delay)
            persist_span.set_attribute("db.system", "postgresql")
            persist_span.set_attribute("db.operation", "INSERT")
            persist_span.set_attribute("db.table", "orders")
            persist_span.add_event("order_persisted", {"order_id": order_id})

        # --- Etapa 3: Notificação (simulada) ---
        with tracer.start_as_current_span(
            "worker.send_notification",
            kind=SpanKind.INTERNAL,
        ) as notify_span:
            notif_delay = random.uniform(0.02, 0.1)
            await asyncio.sleep(notif_delay)
            notify_span.set_attribute("notification.channel", "email")
            notify_span.set_attribute("notification.sent", True)

        elapsed = time.perf_counter() - start
        task_span.set_attribute("worker.total_duration_ms", elapsed * 1000)
        task_span.set_attribute("worker.status", "completed")

        task_duration.record(elapsed, {"priority": priority, "status": "success"})
        tasks_processed.add(1, {"priority": priority, "status": "success"})

        logger.info(
            f"Worker concluiu order_id={order_id} "
            f"total_ms={elapsed*1000:.1f} priority={priority}"
        )

        return {"order_id": order_id, "status": "processed", "duration_ms": elapsed * 1000}


# ---------------------------------------------------------------------------
# Loop Principal do Worker
# ---------------------------------------------------------------------------

async def run_worker():
    """
    Loop principal: aguarda tarefas no Redis com BLPOP e processa uma por vez.
    
    BLPOP: Blocking Left Pop — aguarda até que haja itens na lista.
    Timeout de 1s para permitir que o worker verifique sinais de parada.
    """
    redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    logger.info(f"Worker {WORKER_ID} aguardando tarefas na fila {QUEUE_KEY}...")

    consecutive_errors = 0

    while True:
        try:
            # Aguarda item na fila (blocking, timeout=1s)
            result = await redis.blpop(QUEUE_KEY, timeout=1)

            if result is None:
                # Timeout sem mensagem — continua aguardando
                continue

            queue_depth_gauge.add(-1)
            _, task_json = result

            task_data = json.loads(task_json)
            await process_task(task_data)

            consecutive_errors = 0

        except json.JSONDecodeError as e:
            logger.error(f"Mensagem inválida na fila: {e}")
            consecutive_errors += 1

        except Exception as e:
            logger.error(f"Erro no worker: {e}")
            consecutive_errors += 1

            # Backoff exponencial em caso de erros consecutivos
            if consecutive_errors > 3:
                backoff = min(30, 2**consecutive_errors)
                logger.warning(f"Muitos erros consecutivos. Aguardando {backoff}s")
                await asyncio.sleep(backoff)


async def main():
    await run_worker()


if __name__ == "__main__":
    asyncio.run(main())
