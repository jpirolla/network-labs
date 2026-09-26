# A14 — Internet das Coisas (IoT) com OSPF e DHCP Segmentado

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Laboratório (Cisco Packet Tracer)

## Objetivo

Implementar uma rede com dispositivos **IoT** integrados a uma topologia com **OSPF** e **DHCP centralizado**, segmentando a rede entre a parte de servidores e a parte IoT.

## Etapas

1. Replicar topologia base com IoT
2. Adicionar servidor DNS
3. Dividir a rede em dois segmentos: **Servidores** e **IoT**
4. Configurar **OSPF** para roteamento entre os segmentos
5. Um único servidor **DHCP** distribui endereços para ambos os segmentos

## Conceitos praticados

- **IoT** em Cisco Packet Tracer — dispositivos conectados à rede
- Segmentação de rede: separação lógica entre rede de servidores e rede IoT
- **OSPF** para roteamento entre segmentos distintos
- **DHCP relay** — servidor único atendendo múltiplas redes via `ip helper-address`
- **DNS** integrado à topologia IoT

## Ferramentas

- Cisco Packet Tracer

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.txt` | Especificação da atividade |
| `iot.pkt` | Implementação com IoT + OSPF + DHCP |
