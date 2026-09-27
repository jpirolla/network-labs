Redes de Computadores e Infraestrutura

Repositório com atividades práticas, laboratórios e projetos desenvolvidos durante a graduação em **Ciências da Computação** no ICMC/USP, no âmbito da disciplina **SSC0540 — Redes de Computadores** (2026, Prof. Jó Ueyama).

---

## Organização do repositório

```
network-labs/
├── transport-mux-lab/  → Laboratório de multiplexação na camada de transporte
├── laboratorios/       → 16 atividades práticas da disciplina SSC0540
├── projetos/           → 2 projetos acadêmicos completos (Rede Corporativa Kodalabs)
└── implementacoes/     → Implementações em código Python (DNS Tracer, Observabilidade)
```

---

## Principais conhecimentos praticados

### Redes de Computadores
- Endereçamento IP e subnetting com **VLSM** (Variable Length Subnet Mask)
- Protocolos de roteamento: **RIP v2**, **OSPF** (área única e multi-área), **BGP** (entre Sistemas Autônomos)
- **OSPFv3 com IPv6** (endereçamento /64 e /32, multi-área)
- **VLANs** (IEEE 802.1Q) e roteamento inter-VLAN via **Router-on-a-Stick**
- Serviços de rede: **DHCP** (com relay/`ip helper-address`), **DNS** (split-horizon), **HTTP**, **FTP**, **SMTP**
- **Internet das Coisas (IoT)** — integração com redes OSPF segmentadas
- Topologia hierárquica de três camadas (core, distribuição, acesso)
- Modelo hierárquico com **ABR** (Area Border Router) e **LSDB**
- Comunicação TCP: sockets, portas efêmeras, multiplexação e demultiplexação
- Protocolo DNS em nível de protocolo: wire format, registros A/AAAA/NS/MX (RFC 1035)

### Ferramentas e simuladores
- **Cisco Packet Tracer** — simulação de redes com roteadores, switches e servidores
- **Wireshark** — captura e análise de pacotes DNS, DNS-over-UDP
- **nslookup** — consulta de registros DNS
- **Docker / Docker Compose** — containerização de serviços e infraestrutura
- **Prometheus + Grafana** — coleta e visualização de métricas em tempo real
- **OpenTelemetry / Jaeger / Loki** — rastreamento distribuído e observabilidade

### Programação
- **Python** — sockets TCP/UDP, threads, `select()`, `struct.pack`, FastAPI
- Implementação de protocolo DNS em wire format (sem bibliotecas externas)
- I/O multiplexing com `select()` para servidor TCP concorrente
- Geração de múltiplos fluxos TCP simultâneos com threads
- Instrumentação de métricas com `prometheus_client`
- Tracing distribuído com OpenTelemetry SDK

### Infraestrutura
- **Docker** — Dockerfiles, redes bridge, orquestração com Compose
- Microsserviços com FastAPI, Redis e propagação de contexto de trace
- Configuração de pipeline de observabilidade: OTLP → OTel Collector → Jaeger/Prometheus/Loki

---

## Projetos principais

### [`projetos/projeto1-rede-corporativa`](./projetos/projeto1-rede-corporativa/)
Projeto acadêmico completo: **Rede Corporativa para a Kodalabs** (empresa fictícia com duas unidades — Campinas e São Carlos).

Implementa infraestrutura WAN com: VLAN, VLSM, OSPF, Router-on-a-Stick, DHCP relay, DNS, HTTP, FTP, SMTP. Inclui relatório técnico em LaTeX com justificativas arquiteturais, análise de riscos e validação de conectividade.

### [`projetos/projeto2-wan-multiarea`](./projetos/projeto2-wan-multiarea/)
Evolução do Projeto 1: **OSPF multi-área** (Área 0/1/2, ABR), **Data Center privado** centralizado e integração com **IoT**. Inclui relatório técnico com justificativas de segmentação por VLAN e análise de viabilidade financeira.

### [`transport-mux-lab`](./transport-mux-lab/)
Implementação Python que torna observável o comportamento da **camada de transporte**: múltiplos fluxos TCP simultâneos, `select()` para I/O multiplexing, métricas no Prometheus e dashboards no Grafana.

### [`implementacoes/dns-tracer-lab`](./implementacoes/dns-tracer-lab/)
Ferramenta Python que constrói **pacotes DNS em wire format** (RFC 1035) sem dependências externas. Demonstra compreensão do protocolo em nível de bits e bytes.

### [`implementacoes/observability-lab`](./implementacoes/observability-lab/)
Stack completa de **observabilidade distribuída**: rastreamento com OpenTelemetry/Jaeger, métricas com Prometheus/Grafana, logs com Loki, simulação de falhas caóticas com FastAPI e Redis.

---

## Laboratórios SSC0540

16 atividades práticas progressivas, do básico ao avançado:

| # | Atividade | Principais conceitos |
|---|-----------|----------------------|
| a01 | [LAN com serviços básicos](./laboratorios/a01-lan-servicos-basicos/) | DHCP, DNS, HTTP, Wi-Fi |
| a02 | [Introdução ao Wireshark](./laboratorios/a02-wireshark-intro/) | Análise de pacotes, protocolos |
| a03 | [Interconexão de redes](./laboratorios/a03-interconexao-redes/) | Roteamento, DHCP relay, backbone |
| a04 | [VLSM + RIP v2](./laboratorios/a04-vlsm-rip/) | Subnetting, roteamento dinâmico |
| a05 | [LAN multi-servidor](./laboratorios/a05-lan-multi-servidor/) | HTTP, DNS, e-mail, troubleshooting |
| a06 | [Análise DNS com Wireshark](./laboratorios/a06-wireshark-dns/) | Pacotes DNS, UDP, nslookup |
| a07 | [Interconexão de redes v2](./laboratorios/a07-interconexao-v2/) | Roteamento, serviços distribuídos |
| a08 | [VLSM + RIP v2 (variação)](./laboratorios/a08-vlsm-rip-v2/) | VLSM, ip helper-address |
| a09 | [Subnetting VLSM](./laboratorios/a09-subnetting-vlsm/) | Cálculo de sub-redes |
| a10 | [Subnetting VLSM v2](./laboratorios/a10-subnetting-v2/) | VLSM aplicado em Packet Tracer |
| a11 | [RIP, OSPF e BGP — questionário](./laboratorios/a11-protocolos-roteamento/) | Conceitos teóricos e resolução escrita |
| a12 | [OSPF Multi-área](./laboratorios/a12-ospf-multiarea/) | OSPF Área 0/1/2, DHCP relay, DNS |
| a13 | [VLANs](./laboratorios/a13-vlans/) | IEEE 802.1Q, Switch L2/L3, DHCP |
| a14 | [IoT + OSPF](./laboratorios/a14-iot-ospf/) | IoT, OSPF, segmentação de redes |
| a15 | [OSPFv3 com IPv6](./laboratorios/a15-ospfv3-ipv6/) | IPv6, OSPFv3 multi-área, CLI IOS |


---

## Sobre o repositório

- **Disciplina:** SSC0540 — Redes de Computadores
- **Simulador:** Cisco Packet Tracer (arquivos `.pkt`)
- **Linguagens:** Python, LaTeX, IOS CLI (Cisco)
