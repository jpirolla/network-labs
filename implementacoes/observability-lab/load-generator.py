#!/usr/bin/env python3
"""
load-generator.py
-----------------
Gerador de carga para o Observability Lab.

Envia requisições contínuas ao API Gateway para popular os dashboards
do Grafana e gerar traces visíveis no Jaeger.

Uso:
  python3 load-generator.py                    # padrão: 2 rps, 60s
  python3 load-generator.py --rps 5 --duration 120
  python3 load-generator.py --burst 50          # burst de 50 req
  python3 load-generator.py --gateway http://localhost:8000
"""

import argparse
import asyncio
import json
import random
import time
import sys
try:
    import httpx
except ImportError:
    print("Instale httpx: pip install httpx")
    sys.exit(1)

GATEWAY_URL = "http://localhost:8000"
SAMPLE_ITEMS = ["notebook", "mouse", "teclado", "monitor", "headset", "webcam", "hub-usb", "ssd"]


def random_order() -> dict:
    return {
        "order_id": f"load-{random.randint(10000, 99999)}",
        "items": random.sample(SAMPLE_ITEMS, k=random.randint(1, 4)),
        "priority": random.choice(["normal", "normal", "normal", "high"]),
    }


async def send_order(client: httpx.AsyncClient, gateway: str) -> dict:
    try:
        t0 = time.perf_counter()
        resp = await client.post(f"{gateway}/order", json=random_order(), timeout=12.0)
        latency = (time.perf_counter() - t0) * 1000
        return {"status": resp.status_code, "latency_ms": round(latency, 1)}
    except httpx.TimeoutException:
        return {"status": "TIMEOUT", "latency_ms": None}
    except Exception as e:
        return {"status": f"ERROR:{e}", "latency_ms": None}


async def run_load(gateway: str, rps: float, duration: int):
    interval = 1.0 / rps
    stats = {"200": 0, "503": 0, "504": 0, "other": 0, "latencies": []}
    end_time = time.time() + duration

    print(f"🚀 Iniciando carga: {rps} req/s por {duration}s → {gateway}")
    print(f"{'Status':<10}{'Latência (ms)':<16}{'Progresso'}")
    print("-" * 50)

    async with httpx.AsyncClient() as client:
        req_count = 0
        while time.time() < end_time:
            t_start = time.perf_counter()
            result = await send_order(client, gateway)
            req_count += 1

            status = str(result["status"])
            lat = result.get("latency_ms")
            elapsed = int(time.time() - (end_time - duration))

            if status == "200":
                stats["200"] += 1
                icon = "✅"
            elif status == "503":
                stats["503"] += 1
                icon = "⚠️ "
            elif status == "504":
                stats["504"] += 1
                icon = "⏱️ "
            else:
                stats["other"] += 1
                icon = "❌"

            if lat:
                stats["latencies"].append(lat)

            print(f"{icon} {status:<8} {str(lat)+'ms':<16} [{elapsed}s/{duration}s] req#{req_count}")

            # Aguarda até o próximo ciclo
            elapsed_req = time.perf_counter() - t_start
            sleep_time = max(0, interval - elapsed_req)
            await asyncio.sleep(sleep_time)

    # Estatísticas finais
    total = req_count
    lats = stats["latencies"]
    lats_sorted = sorted(lats) if lats else [0]

    print("\n" + "=" * 50)
    print("📊 ESTATÍSTICAS FINAIS")
    print("=" * 50)
    print(f"Total de requisições: {total}")
    print(f"  ✅ Sucesso (200):    {stats['200']} ({stats['200']/total*100:.1f}%)")
    print(f"  ⚠️  Erro (503):       {stats['503']} ({stats['503']/total*100:.1f}%)")
    print(f"  ⏱️  Timeout (504):    {stats['504']} ({stats['504']/total*100:.1f}%)")
    print(f"  ❌ Outros:           {stats['other']} ({stats['other']/total*100:.1f}%)")
    if lats:
        p50 = lats_sorted[int(len(lats_sorted) * 0.50)]
        p95 = lats_sorted[int(len(lats_sorted) * 0.95)]
        p99 = lats_sorted[int(len(lats_sorted) * 0.99)]
        print(f"\nLatência (apenas sucessos):")
        print(f"  p50: {p50:.0f}ms | p95: {p95:.0f}ms | p99: {p99:.0f}ms")
    print("\n🔍 Veja os traces em: http://localhost:16686")
    print("📈 Veja as métricas em: http://localhost:3000")


async def burst(gateway: str, count: int):
    print(f"💥 Enviando burst de {count} requisições simultâneas...")
    async with httpx.AsyncClient() as client:
        tasks = [send_order(client, gateway) for _ in range(count)]
        results = await asyncio.gather(*tasks)

    success = sum(1 for r in results if r["status"] == 200)
    fail = count - success
    print(f"✅ Sucesso: {success} | ❌ Falha: {fail}")


def main():
    parser = argparse.ArgumentParser(description="Load Generator — Observability Lab")
    parser.add_argument("--gateway", default=GATEWAY_URL, help="URL do API Gateway")
    parser.add_argument("--rps", type=float, default=2.0, help="Requisições por segundo")
    parser.add_argument("--duration", type=int, default=60, help="Duração em segundos")
    parser.add_argument("--burst", type=int, default=0, help="Enviar N requisições simultâneas")
    args = parser.parse_args()

    if args.burst > 0:
        asyncio.run(burst(args.gateway, args.burst))
    else:
        asyncio.run(run_load(args.gateway, args.rps, args.duration))


if __name__ == "__main__":
    main()
