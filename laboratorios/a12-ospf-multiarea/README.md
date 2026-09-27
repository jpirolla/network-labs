# A12 — OSPF Multi-área com DHCP Centralizado

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Laboratório (Cisco Packet Tracer)

## Objetivo

Implementar uma rede com protocolo de roteamento **OSPF em múltiplas áreas** (Área 0, 1 e 2), garantindo comunicação entre todos os segmentos e serviço de **DHCP centralizado** com relay entre áreas.

## Topologia

```
[Área 1]
  Redes locais
      │
  [ABR] ──── [Área 0 — Backbone] ──── [ABR]
                                           │
                                       [Área 2]
                                         Redes locais + Servidor DHCP/DNS (192.168.1.2)
```

## Conceitos praticados

- **OSPF multi-área**: Área 0 (backbone), Área 1 e Área 2
- **ABR** (Area Border Router) — roteadores nas fronteiras de área
- Verificação de adjacências com comandos de diagnóstico:
  - `show ip ospf neighbor`
  - `show ip ospf interface`
  - `show ip ospf database`
  - `show ip route`
- **DHCP centralizado** com relay entre áreas OSPF
- Servidor DNS na rede `192.168.1.66`
- Acesso HTTP ao servidor web (`192.168.1.2`)
- Expansão (desafio): Áreas 3 e 4 adicionais comunicando pela Área 0

## Comandos Cisco IOS utilizados

```
show ip ospf neighbor
show ip ospf interface
show ip ospf database
show ip route
```

## Ferramentas

- Cisco Packet Tracer

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.md` | Especificação completa (Parte 1 + Desafio) |
| `ospf1.pkt` | Implementação OSPF multi-área no Packet Tracer |
| `lab-19mai.zip` | Material complementar do laboratório |
