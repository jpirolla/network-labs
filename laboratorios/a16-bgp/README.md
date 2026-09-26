# A16 — Protocolo BGP entre Sistemas Autônomos

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Laboratório (Cisco Packet Tracer)

## Objetivo

Implementar e configurar o protocolo **BGP** (Border Gateway Protocol) entre diferentes **Sistemas Autônomos (AS)**, adicionando servidores DHCP e DNS em ASes específicos.

## Etapas

1. Elaborar a topologia conforme especificação em PDF
2. Configurar BGP conforme os comandos indicados no arquivo em anexo
3. Adicionar servidor **DHCP** na AS 700
4. Adicionar servidor **DNS** na AS 800

## Conceitos praticados

- **BGP** (Border Gateway Protocol) — protocolo de roteamento entre Sistemas Autônomos
- **Sistemas Autônomos (AS)** — identificação e roteamento entre domínios distintos
- **eBGP** (BGP externo) — sessões entre roteadores de diferentes ASes
- Integração de DHCP e DNS em redes BGP
- Configuração via CLI IOS Cisco

## Contexto teórico

O BGP é o protocolo que interliga os Sistemas Autônomos na Internet. Enquanto OSPF e RIP cuidam do roteamento *dentro* de um AS (IGPs), o BGP cuida do roteamento *entre* ASes (EGP). Esta atividade representa o nível mais alto da hierarquia de roteamento estudada na disciplina.

## Ferramentas

- Cisco Packet Tracer

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.txt` | Especificação da atividade |
| `aula12jun.pkt` | Implementação BGP no Cisco Packet Tracer |
| `bgp_lab_especificacao.pdf` | Especificação detalhada com topologia e comandos BGP |
