# A09 — Subnetting VLSM — Cálculo de Sub-redes

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Exercício teórico + Packet Tracer

## Objetivo

Dividir a rede `192.168.1.0/24` em **5 sub-redes** com capacidades específicas, aplicando os princípios de VLSM.

## Especificação

Requisitos de capacidade:

| Sub-rede | Hosts necessários | CIDR resultante |
|----------|-------------------|-----------------|
| 3 sub-redes | 62 hosts cada | /26 |
| 1 sub-rede | 30 hosts | /27 |
| 1 sub-rede | 2 hosts | /30 |

Para cada sub-rede, deve ser informado: sub-rede, CIDR, endereço de rede, máscara e intervalo de hosts válidos.

## Conceitos praticados

- **VLSM** (Variable Length Subnet Mask) — alocação eficiente de endereços
- Cálculo de endereçamento: rede, broadcast e hosts válidos
- **CIDR** — notação com prefixo
- Não sobreposição de endereços entre sub-redes
- Pertencimento ao bloco original (`192.168.1.0/24`)

## Relação com redes

O domínio de VLSM é essencial para:
- Planejar redes corporativas sem desperdício de endereços
- Justificar escolhas de máscara por departamento/função
- Preparar tabelas de endereçamento para projetos como o Projeto 1 (Kodalabs)

## Ferramentas

- Cisco Packet Tracer

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.md` | Especificação com requisitos de sub-redes |
| `10abril_projeto4.pkt` | Implementação no Cisco Packet Tracer |
