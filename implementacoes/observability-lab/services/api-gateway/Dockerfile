FROM python:3.12-slim

WORKDIR /app

# Copia dependências primeiro (cache de camadas Docker)
COPY api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared /app/shared
COPY api-gateway/ .

EXPOSE 8000

# CONCEITO: opentelemetry-instrument (zero-code instrumentation)
# É possível rodar sem modificar o código usando a CLI:
#   opentelemetry-instrument uvicorn main:app
# Mas aqui usamos SDK diretamente para ter controle total e fins didáticos.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"]
