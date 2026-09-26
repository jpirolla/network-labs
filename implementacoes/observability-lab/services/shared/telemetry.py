"""
shared/telemetry.py
-------------------
Módulo compartilhado de setup do OpenTelemetry.

Este módulo centraliza toda a inicialização do SDK OpenTelemetry:
  - TracerProvider com exportador OTLP para o Collector
  - MeterProvider com exportador OTLP para o Collector
  - Formatter de log JSON que injeta trace_id e span_id automaticamente

CONCEITO: Por que centralizar?
  Em produção, cada serviço teria seu próprio setup, mas com a mesma lógica.
  Centralizar aqui evita repetição e garante consistência entre serviços.
"""

import logging
import json
import os
import sys
from typing import Optional

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter


# ---------------------------------------------------------------------------
# JSON Log Formatter com injeção de trace context
# ---------------------------------------------------------------------------

class OTelJSONFormatter(logging.Formatter):
    """
    Formatter que serializa cada log record como JSON estruturado e injeta
    automaticamente trace_id e span_id do span ativo no OpenTelemetry.

    CONCEITO: Correlação Traces ↔ Logs
      No Grafana, combinando Loki (logs) + Jaeger (traces), é possível
      navegar de um log diretamente para o trace correspondente, pois ambos
      compartilham o mesmo trace_id.
    """

    def format(self, record: logging.LogRecord) -> str:
        # Captura o span atual do contexto OTel
        current_span = trace.get_current_span()
        ctx = current_span.get_span_context()

        # Formata trace_id e span_id como hex (formato padrão W3C)
        trace_id = (
            format(ctx.trace_id, "032x") if ctx.is_valid else "00000000000000000000000000000000"
        )
        span_id = (
            format(ctx.span_id, "016x") if ctx.is_valid else "0000000000000000"
        )

        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": trace_id,
            "span_id": span_id,
            "service": os.getenv("SERVICE_NAME", "unknown"),
        }

        # Inclui informações de exceção, se houver
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)


def setup_logging(service_name: str) -> logging.Logger:
    """Configura o logging estruturado JSON para o serviço."""
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(OTelJSONFormatter())
    logger.addHandler(handler)

    # Silencia loggers barulhentos de libs externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logger


# ---------------------------------------------------------------------------
# OTel SDK Setup
# ---------------------------------------------------------------------------

def setup_telemetry(
    service_name: str,
    service_version: str = "1.0.0",
    otlp_endpoint: Optional[str] = None,
) -> tuple:
    """
    Inicializa e registra globalmente o TracerProvider e MeterProvider.

    Args:
        service_name: Nome do serviço (aparecerá no Jaeger e Prometheus).
        service_version: Versão do serviço (bom para correlação de deploys).
        otlp_endpoint: Endpoint gRPC do OTel Collector.
                       Default: OTEL_EXPORTER_OTLP_ENDPOINT env var ou localhost:4317.

    Returns:
        Tupla (tracer, meter) prontos para uso.

    CONCEITO: Resource
      Um Resource descreve *quem* está gerando a telemetria. É o equivalente
      a "metadata do serviço" e aparece em todos os traces, métricas e logs
      associados a este processo.
    """
    endpoint = otlp_endpoint or os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
    )

    # Resource: identifica este serviço em toda a telemetria
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
    })

    # --- Tracing ---
    # CONCEITO: BatchSpanProcessor
    #   Não exporta cada span individualmente (seria lento).
    #   Acumula spans em lote e envia em intervalos regulares.
    #   Em produção, ajusta-se max_export_batch_size e schedule_delay_millis.
    tracer_provider = TracerProvider(resource=resource)
    otlp_span_exporter = OTLPSpanExporter(
        endpoint=endpoint,
        insecure=True,  # TLS desabilitado para demo; em produção use certificados
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_span_exporter))
    trace.set_tracer_provider(tracer_provider)

    # --- Metrics ---
    # CONCEITO: PeriodicExportingMetricReader
    #   Coleta métricas em intervalos regulares (default: 60s).
    #   Para dashboards em tempo real, use intervalos menores (ex: 10s).
    otlp_metric_exporter = OTLPMetricExporter(
        endpoint=endpoint,
        insecure=True,
    )
    metric_reader = PeriodicExportingMetricReader(
        otlp_metric_exporter,
        export_interval_millis=10_000,  # 10s para demo
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    tracer = trace.get_tracer(service_name)
    meter = metrics.get_meter(service_name)

    return tracer, meter
