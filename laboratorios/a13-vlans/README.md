# A13 — VLANs com Switch L2/L3 e DHCP

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Laboratório (Cisco Packet Tracer)

## Objetivo

Implementar dois projetos de VLANs com abordagens distintas (Switch L2 e Switch L3), integrando serviço de **DNS**.

## Projetos implementados

### 1. VLANs com Switch L2 + DHCP no Roteador
- VLANs configuradas em switch de camada 2
- DHCP servido pelo roteador (não pelo servidor)
- Trunk entre switch e roteador para transportar múltiplas VLANs

### 2. VLANs com Switch L3 + DHCP
- VLANs configuradas em switch multicamada (Layer 3)
- Roteamento inter-VLAN realizado pelo próprio switch (sem Router-on-a-Stick)
- DHCP centralizado

### 3. Adição de servidor DNS
- DNS inserido na topologia para resolução de nomes entre as VLANs

## Conceitos praticados

- **VLANs** (IEEE 802.1Q) — segmentação lógica de redes
- Diferença entre Switch L2 e Switch L3 para roteamento inter-VLAN
- Portas **access** e **trunk** em switches
- DHCP no roteador vs. servidor DHCP dedicado
- Integração de **DNS** em redes segmentadas por VLAN

## Ferramentas

- Cisco Packet Tracer

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.md` | Especificação dos três projetos |
| `lab-19mai/` | Arquivos `.pkt` do laboratório (lab-19mai.pkt e lab-19mai-pt2.pkt) |
