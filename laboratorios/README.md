# Laboratórios — SSC0540 Redes de Computadores

Atividades práticas realizadas durante a disciplina **SSC0540 — Redes de Computadores** (ICMC/USP, 2026, Prof. Jó Ueyama).

As atividades utilizam o simulador **Cisco Packet Tracer** (arquivos `.pkt`) e cobrem progressivamente os conceitos fundamentais de redes de computadores, do endereçamento básico até protocolos de roteamento avançados.

Cada pasta contém:
- `enunciado.txt` — especificação original da atividade
- `*.pkt` — implementação no Cisco Packet Tracer (quando aplicável)
- `*.pdf` — material de apoio ou roteiro (quando disponível)
- `README.md` — descrição da atividade e conceitos praticados

---

## Conceitos praticados ao longo das atividades

- Endereçamento IP e subnetting com VLSM
- Serviços de rede: DHCP, DNS, HTTP, FTP, SMTP, e-mail
- Protocolos de roteamento: RIP v2, OSPF (área única e multi-área), BGP
- OSPFv3 com IPv6
- VLANs (IEEE 802.1Q) e roteamento inter-VLAN
- DHCP relay com `ip helper-address`
- Análise de pacotes com Wireshark
- Configuração de roteadores via CLI IOS (Cisco)
- Internet das Coisas (IoT) integrada a redes OSPF
- BGP entre Sistemas Autônomos

---

## Atividades

| # | Atividade | Conceitos principais | Ferramentas | Tipo | Complexidade |
|---|-----------|----------------------|-------------|------|-------------|
| [a01](./a01-lan-servicos-basicos/) | LAN com serviços básicos | DHCP, DNS, HTTP, Wi-Fi | Packet Tracer | Lab | Básica |
| [a02](./a02-wireshark-intro/) | Introdução ao Wireshark | Análise de pacotes, protocolos | Wireshark | Lab | Básica |
| [a03](./a03-interconexao-redes/) | Interconexão de redes | Roteamento, DHCP relay, fibra | Packet Tracer | Lab | Média |
| [a04](./a04-vlsm-rip/) | VLSM + RIP v2 | Subnetting, roteamento dinâmico | Packet Tracer | Lab | Média |
| [a05](./a05-lan-multi-servidor/) | LAN multi-servidor | HTTP, DNS, e-mail, troubleshooting | Packet Tracer | Lab | Média |
| [a06](./a06-wireshark-dns/) | Análise DNS com Wireshark | Pacotes DNS, UDP, nslookup, ipconfig | Wireshark | Lab | Média |
| [a07](./a07-interconexao-v2/) | Interconexão de redes v2 | Roteamento, serviços distribuídos | Packet Tracer | Lab | Média |
| [a08](./a08-vlsm-rip-v2/) | VLSM + RIP v2 (variação) | VLSM, ip helper-address | Packet Tracer | Lab | Média |
| [a09](./a09-subnetting-vlsm/) | Subnetting VLSM | Cálculo de sub-redes, CIDR | Packet Tracer | Exercício | Básica |
| [a10](./a10-subnetting-v2/) | Subnetting VLSM v2 | VLSM aplicado | Packet Tracer | Lab | Básica |
| [a11](./a11-protocolos-roteamento/) | RIP, OSPF e BGP — questionário | Conceitos teóricos, resolução escrita | — | Escrita | Média |
| [a12](./a12-ospf-multiarea/) | OSPF Multi-área | Área 0/1/2, DHCP relay, `show ip ospf` | Packet Tracer | Lab | Alta |
| [a13](./a13-vlans/) | VLANs | IEEE 802.1Q, Switch L2/L3, DHCP | Packet Tracer | Lab | Média-Alta |
| [a14](./a14-iot-ospf/) | IoT + OSPF | IoT, OSPF, segmentação | Packet Tracer | Lab | Alta |
| [a15](./a15-ospfv3-ipv6/) | OSPFv3 com IPv6 | IPv6, OSPFv3 multi-área, CLI IOS | Packet Tracer | Lab | Alta |
| [a16](./a16-bgp/) | BGP entre Sistemas Autônomos | BGP, AS, eBGP | Packet Tracer | Lab | Alta |
