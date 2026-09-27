# A04 — VLSM com DHCP, DNS e RIP v2

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Laboratório (Cisco Packet Tracer)

## Objetivo

Implementar uma rede baseada em `192.168.1.0/24` aplicando **VLSM** (Variable Length Subnet Mask) para subdividir o espaço de endereçamento sem sobreposição, com **RIP v2** como protocolo de roteamento dinâmico.

## Topologia e endereçamento

| Segmento | Sub-rede | Capacidade |
|----------|----------|------------|
| LAN 1 | 192.168.1.0/26 | 62 hosts |
| LAN 2 | 192.168.1.64/26 | 62 hosts |
| Link entre roteadores | 192.168.1.252/30 | 2 hosts |
| LAN 3 (desafio) | 192.168.1.224/27 | 30 hosts |

## Conceitos praticados

- **VLSM** — subdivisão de rede com máscaras de comprimento variável
- **RIP v2** — protocolo de roteamento por vetor de distância, sem auto-summary
- **DHCP** — distribuição automática de IPs para todas as LANs
- **DHCP relay** com `ip helper-address` para redes remotas
- **DNS** — registro de nome para servidor da LAN 2
- Configuração de roteadores: interfaces, protocolo `router rip`, `version 2`, `no auto-summary`

## Comandos Cisco IOS utilizados

```
router rip
version 2
no auto-summary
network 192.168.1.0
```

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.md` | Especificação da atividade (VLSM + RIP v2) |
| `resolucao-protocolos.txt` | Resolução escrita do questionário sobre RIP/OSPF/BGP |
| `pratica_lab_http.pdf` | Material de apoio do laboratório |
