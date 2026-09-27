# A15 — OSPFv3 com IPv6 Multi-área

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Laboratório (Cisco Packet Tracer)

## Objetivo

Implementar uma rede **IPv6** com roteamento **OSPFv3** em múltiplas áreas (Área 0, 1 e 2), configurando roteadores Cisco ISR 4331 via CLI IOS.

## Topologia

```
                   [Área 0]
         2001:0:1::/64    2001:0:2::/64
              │                │
[R1] ──────[R0]──────[R2]
  │   gig0/0/0  gig0/0/1   │
  │                         │
[Área 1]              [Área 2]
2001:1:1::/64         2001:2:1::/64
```

**Roteadores:** ISR 4331 (suporte a IPv6)

## Conceitos praticados

- **IPv6** — endereçamento com prefixo /64 e /32
- **OSPFv3** (OSPF para IPv6) — configuração em múltiplas áreas
- `router-id` manual para identificação dos roteadores
- Configuração de interfaces com `ipv6 ospf 1 area X`
- `ipv6 unicast-routing` — habilitação de roteamento IPv6
- Conectividade entre áreas via Área 0 (backbone)
- `ping` entre dispositivos em áreas diferentes

## Comandos Cisco IOS utilizados

```
ipv6 unicast-routing
ipv6 router ospf 1
router-id 10.0.0.X
interface gig 0/0/0
  ipv6 enable
  ipv6 ospf 1 area 0
  ipv6 address 2001:0:1::1/64
  no shutdown
```

> O enunciado desta atividade contém o roteiro completo de configuração dos três roteadores.

## Ferramentas

- Cisco Packet Tracer
- CLI IOS (Cisco)

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.md` | Roteiro completo com comandos CLI para os 3 roteadores |
| `aula19jun.pkt` | Implementação OSPFv3 IPv6 no Packet Tracer |
