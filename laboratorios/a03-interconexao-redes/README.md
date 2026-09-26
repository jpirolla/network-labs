# A03 — Interconexão de Redes usando Roteadores

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Laboratório (Cisco Packet Tracer)

## Objetivo

Projetar e implementar uma infraestrutura com **duas sub-redes distintas** interligadas por um backbone de alta velocidade, com serviços de rede distribuídos entre servidores dedicados.

## Topologia

```
[Rede 1: 192.168.1.0/24]              [Rede 2: 192.168.2.0/24]
  Switch + Servidores (DHCP/Web/Mail)   Switch + Servidor DNS
         └──── fibra óptica ────┐
                           [Roteador central]
                           └──── fibra óptica ────┘
```

## Conceitos praticados

- Interconexão de redes via roteador com duas interfaces
- Endereçamento IP em múltiplas redes (192.168.1.0/24 e 192.168.2.0/24)
- **DHCP relay** (`ip helper-address`) — servidor DHCP em uma rede atendendo outra rede
- **DNS** dedicado em rede separada
- Serviços distribuídos: DHCP + HTTP + e-mail na Rede 1; DNS na Rede 2
- Backbone com fibra óptica (Gigabit Ethernet)
- Roteamento estático entre sub-redes

## Ferramentas

- Cisco Packet Tracer

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.txt` | Especificação completa (topologia, endereçamento, serviços) |
| `pratica2.pkt` | Implementação no Cisco Packet Tracer |
