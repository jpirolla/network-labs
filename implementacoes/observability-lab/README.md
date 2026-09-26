# 🔭 Observability Lab — Distributed Tracing with OpenTelemetry

> **Portfolio project** demonstrating production-grade distributed observability: distributed tracing, metrics correlation, structured logging, and chaos engineering across a FastAPI microservices architecture.

**Stack**: Python · FastAPI · OpenTelemetry · Jaeger · Prometheus · Grafana · Loki · Redis · Docker

---

## 📐 Architecture

```
                        ┌─────────────────────────────────────┐
                        │           Client / LoadGen           │
                        └──────────────────┬──────────────────┘
                                           │ HTTP POST /order
                                           ▼
                        ┌─────────────────────────────────────┐
                        │         API Gateway :8000            │
                        │  FastAPI + OTel auto + manual spans  │
                        │  Metrics: requests_total, latency    │
                        └───────────────┬─────────────────────┘
                                        │ HTTP + traceparent header
                                        ▼
                        ┌─────────────────────────────────────┐
                        │         Service A :8001              │
                        │  Order Processor                     │
                        │  Extracts trace ctx → child spans    │
                        │  Calls Service B + enqueues Redis    │
                        └──────┬────────────────┬─────────────┘
                               │ HTTP            │ Redis RPUSH
                               ▼                 ▼
          ┌────────────────────────┐   ┌─────────────────────┐
          │     Service B :8002    │   │     Worker           │
          │   External Simulator   │   │  Redis BLPOP         │
          │   Random: 100–2000ms   │   │  Async trace prop.   │
          │   20% errors, 10% TO   │   │  3 child spans       │
          └────────────────────────┘   └─────────────────────┘
                               │
              ┌────────────────▼──────────────────────┐
              │        OTel Collector :4317            │
              │  Pipeline: OTLP → batch → multi-export│
              └────────┬──────────────┬───────────────┘
                       │              │              │
                       ▼              ▼              ▼
               ┌────────────┐  ┌──────────┐  ┌──────────┐
               │   Jaeger   │  │ Prometheus│  │   Loki   │
               │  :16686    │  │  :9090   │  │  :3100   │
               └────────────┘  └──────────┘  └──────────┘
                                    │
                             ┌──────▼──────┐
                             │   Grafana   │
                             │   :3000     │
                             └─────────────┘
```

---

## 🚀 Quickstart

```bash
# 1. Clone e entre no diretório
cd network-labs/observability-lab

# 2. Suba toda a stack
docker compose up -d --build

# 3. Aguarde os serviços ficarem saudáveis (~30s)
docker compose ps

# 4. Envie um pedido de teste
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{"order_id": "test-001", "items": ["notebook", "mouse"], "priority": "high"}'

# 5. Abra o Jaeger e veja o trace
open http://localhost:16686

# 6. Abra o Grafana (admin/admin)
open http://localhost:3000
```

### Gerar carga contínua

```bash
# Instale httpx localmente
pip install httpx

# 2 req/s por 60 segundos
python3 load-generator.py

# 5 req/s por 2 minutos
python3 load-generator.py --rps 5 --duration 120

# Burst de 30 requisições simultâneas
python3 load-generator.py --burst 30
```

---

## 🔍 O que Observar

### No Jaeger (`http://localhost:16686`)

1. **Selecione** o serviço `api-gateway` → **Find Traces**
2. Clique num trace → você verá uma **cascata de spans**:

```
api-gateway: POST /order                    [root span, ~500ms–2s]
  ├─ validate_request                       [~5ms]
  └─ call_service_a                         [~400ms–2s]
       ├─ service-a: POST /process          [auto-span]
       │    ├─ process_order_items          [~20–150ms]
       │    ├─ call_service_b_enrichment    [~100–2000ms] ← aqui mora a latência
       │    │    └─ service-b: POST /enrich [auto-span]
       │    │         └─ external_data_fetch [latência aleatória]
       │    └─ enqueue_worker_task          [~1ms]
       └─ worker: process_task             [async, ~150–800ms]
            ├─ worker.enrich_data          [~100–400ms]
            ├─ worker.persist_to_db        [~50–300ms]
            └─ worker.send_notification    [~20–100ms]
```

3. **Filtre traces com erro**: `Tags: error=true` → veja spans vermelhos

### No Grafana (`http://localhost:3000`)

| Dashboard Panel | O que mostra |
|---|---|
| Throughput por Serviço | req/s por serviço ao longo do tempo |
| Taxa de Erro — Service B | Gauge: % de erros (alvo: ~20%) |
| Latência p50/p95/p99 | Distribuição de latência (cauda longa do Service B) |
| Worker — Throughput | Tarefas/s processadas assincronamente |
| Logs de Erro | Logs JSON com `trace_id` clicável |

### No Prometheus (`http://localhost:9090`)

```promql
# Latência p95 do API Gateway
histogram_quantile(0.95, rate(otel_gateway_request_duration_seconds_bucket[5m]))

# Taxa de erro do Service B
rate(otel_service_b_errors_total[5m]) / rate(otel_service_b_requests_total[5m])

# Throughput do worker
rate(otel_worker_tasks_processed_total[1m])
```

---

## 🧠 Conceitos Fundamentais

### 1. Propagação de Contexto (Context Propagation)

O **trace_id** nunca muda durante toda a jornada de uma requisição. O que muda é o **span_id** — cada serviço cria seu próprio span filho.

```
traceparent: 00-{trace_id}-{parent_span_id}-{flags}
             ^^  ^^^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^^^^
             version   128-bit trace ID     01=sampled
```

O `FastAPIInstrumentor` e o `HTTPXClientInstrumentor` injetam/extraem esse header automaticamente. O `extract()` manual é necessário para filas e outros canais assíncronos.

### 2. Instrumentação Automática vs Manual

| Aspecto | Automática | Manual |
|---|---|---|
| **O que captura** | Spans HTTP, DB, Redis genéricos | Spans com semântica de negócio |
| **Exemplo** | `POST /order` com status code | `validate_request` com `order.priority` |
| **Atributos** | URL, método, status | Qualquer campo que você definir |
| **Esforço** | Zero (1 linha de código) | Médio (tracer.start_as_current_span) |
| **Valor** | Visibilidade base | Diagnóstico profundo |
| **Em produção** | Sempre | Para fluxos críticos de negócio |

**Regra prática**: Use automática como base. Adicione spans manuais nos caminhos críticos onde você precisa de diagnóstico de negócio.

### 3. Os Três Pilares da Observabilidade

```
Traces  → "O que aconteceu?" (sequência causal de operações)
Métricas → "Com que frequência?" (agregação temporal)
Logs    → "Qual o contexto?" (detalhes com trace_id para correlação)
```

No Grafana, é possível navegar: **Log com trace_id** → **Trace no Jaeger** → **Métrica no Prometheus** — tudo correlacionado pelo mesmo `trace_id`.

### 4. O OTel Collector Como Hub Central

```
Serviços → [OTLP gRPC] → Collector → Jaeger (traces)
                                   → Prometheus (métricas via exporter)
                                   → Loki (logs)
```

**Vantagem estratégica**: Se você trocar Jaeger por Grafana Tempo, ou Prometheus por VictoriaMetrics, **nenhum serviço muda** — apenas a config do Collector.

### 5. SpanKind — Semântica de Comunicação

| Kind | Quando usar | Exemplo |
|---|---|---|
| `SERVER` | Recebendo chamada HTTP (server-side) | `api-gateway: POST /order` |
| `CLIENT` | Fazendo chamada HTTP (client-side) | `call_service_a` |
| `PRODUCER` | Publicando mensagem em fila | `enqueue_worker_task` |
| `CONSUMER` | Consumindo mensagem de fila | `worker.process_task` |
| `INTERNAL` | Operação interna do serviço | `validate_request` |

---

## 🔥 Simulação de Falhas

O Service B possui comportamento caótico configurável via env vars:

```bash
# Aumentar taxa de erros para 50%
docker compose up service-b -e ERROR_RATE=0.50

# Desabilitar timeouts temporariamente
docker compose up service-b -e TIMEOUT_RATE=0.00

# Simular serviço lento (latência mínima 1s)
docker compose up service-b -e MIN_LATENCY_MS=1000 -e MAX_LATENCY_MS=5000
```

### Observando falhas no Jaeger

Traces com erro aparecem em **vermelho**. Ao inspecionar:
- `span.status = ERROR` com mensagem descritiva
- `span.events` com stack trace (via `record_exception()`)
- Atributos: `simulation.type`, `simulation.latency_ms`

---

## 📁 Estrutura do Projeto

```
observability-lab/
├── docker-compose.yml              # Stack completa
├── load-generator.py               # Gerador de carga para testes
├── services/
│   ├── shared/
│   │   └── telemetry.py            # Setup OTel compartilhado (tracer + meter + logs)
│   ├── api-gateway/
│   │   ├── main.py                 # Gateway com spans manuais e métricas customizadas
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── service-a/
│   │   ├── main.py                 # Processador com propagação e enqueue Redis
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── service-b/
│   │   ├── main.py                 # Simulador caótico (latência + erros)
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── worker/
│       ├── worker.py               # Consumer Redis com propagação async de trace
│       ├── requirements.txt
│       └── Dockerfile
└── infra/
    ├── otel-collector-config.yaml  # Pipeline: OTLP → Jaeger + Prometheus + Loki
    ├── prometheus.yml              # Scrape configs
    ├── loki-config.yaml            # Backend de logs
    └── grafana/
        ├── provisioning/
        │   ├── datasources/        # Auto-provisionamento: Prometheus, Jaeger, Loki
        │   └── dashboards/
        └── dashboards/
            └── observability-lab.json  # Dashboard pré-construído
```

---

## 🛠️ Operações Úteis

```bash
# Ver logs de um serviço específico (JSON estruturado)
docker compose logs api-gateway --follow | python3 -m json.tool

# Verificar trace_id nos logs
docker compose logs service-a | grep -o '"trace_id":"[^"]*"'

# Reiniciar apenas o Service B com nova config de caos
docker compose restart service-b

# Inspecionar métricas brutas do Collector
curl http://localhost:8889/metrics | grep otel_

# Verificar fila Redis
docker compose exec redis redis-cli LLEN worker:tasks

# Parar e limpar tudo (inclusive volumes)
docker compose down -v
```

---

## 🏭 Considerações de Produção

| Aspecto | Demo (aqui) | Produção |
|---|---|---|
| **Sampling** | 100% dos traces | 1–10% (head-based) ou por criticidade (tail-based) |
| **TLS** | Desabilitado | Necessário no Collector e entre serviços |
| **Autenticação Grafana** | admin/admin | SSO/LDAP |
| **Retenção Jaeger** | Em memória | Cassandra ou Elasticsearch com TTL |
| **Retenção Prometheus** | 7 dias (volume local) | Thanos ou Cortex para longo prazo |
| **Collector Scale** | 1 instância | Deployment + load balancer |
| **Secrets** | Env vars no compose | Vault, AWS Secrets Manager |
| **Alerting** | Dashboards visuais | AlertManager + PagerDuty |

---

## 📚 Referências

- [OpenTelemetry Python SDK](https://opentelemetry-python.readthedocs.io/)
- [W3C TraceContext Specification](https://www.w3.org/TR/trace-context/)
- [OTel Collector Configuration](https://opentelemetry.io/docs/collector/configuration/)
- [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Cindy Sridharan — Distributed Systems Observability](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/)
