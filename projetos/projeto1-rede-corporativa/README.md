# Projeto 1 — Rede Corporativa para a Kodalabs

**Disciplina:** SSC0540 — Redes de Computadores | ICMC/USP  
**Professor:** Jó Ueyama  
**Tipo:** Projeto acadêmico completo com relatório técnico em LaTeX

---

## Objetivo

Projetar e implementar a infraestrutura de rede WAN para a **Kodalabs**, consultoria de engenharia de dados com duas unidades: **Campinas** (matriz) e **São Carlos** (filial).

## Cenário

- **Campinas (matriz):** ~15 colaboradores técnicos; servidor centralizado com DNS, DHCP, HTTP, FTP, SMTP
- **São Carlos (filial):** ~10 colaboradores administrativos; sem servidores locais, consome tudo via WAN

## Conceitos praticados

### Endereçamento e Segmentação
- **VLSM** — subdivisão hierárquica do bloco `192.168.10.0/24` (Campinas) e `192.168.60.0/24` (São Carlos)
- **VLANs** (IEEE 802.1Q) — 9 VLANs departamentais (Engenharia de Dados, Data Science, TI, Servidores, Visitantes em cada unidade)

### Roteamento
- **OSPF** (área 0 única) — roteamento dinâmico WAN entre as duas localidades
- **Router-on-a-Stick** (subinterfaces 802.1Q) — roteamento inter-VLAN em interface física única
- `passive-interface default` + `no passive-interface` na interface WAN (segurança)

### Serviços de Rede
- **DHCP** centralizado em Campinas com relay (`ip helper-address`) atendendo 9 VLANs de duas localidades
- **DNS** em modo split-horizon (`kodalabs.com.br` interno + forwarder externo `8.8.8.8`)
- **HTTP**, **FTP**, **SMTP** — servidor virtualizado centralizado

### Topologia
- Modelo hierárquico de **3 camadas** (core, distribuição, acesso)
- Topologia **estrela estendida** com switches de core dedicados
- Link WAN `11.0.0.0/30` entre roteadores

## Validação

Testes realizados (documentados no relatório):
- `ping` intra-VLAN, inter-VLAN e entre localidades (TTL decremental)
- `tracert` confirmando 3 hops Campinas → São Carlos
- `show ip ospf neighbor` (estado FULL)
- `show ip route` (rotas OSPF marcadas com 'O')
- Acesso HTTP via nome DNS (`www.kodalabs.com.br`)
- Obtenção de IP via DHCP por clientes de São Carlos (relay WAN)

## Como visualizar

Abra o arquivo `projeto1.pkt` no **Cisco Packet Tracer** (versão 8.x recomendada).

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `projeto1.pkt` | Implementação completa no Cisco Packet Tracer |
| `relatorio.pdf` | Relatório técnico compilado (LaTeX) |
| `latex-p1.tex` | Código-fonte LaTeX do relatório |
| `img/` | Capturas de tela usadas no relatório (configurações e testes) |
| `link_gravacao.txt` | Link para vídeo de apresentação |
| `Roteiro de Apresentação — Rede Kodalabs.pdf` | Roteiro utilizado na apresentação |

## Aprendizados

- Planejamento de endereçamento IP para rede corporativa real (VLSM com justificativas por departamento)
- Configuração de OSPF com `passive-interface` para segurança
- Entendimento do fluxo completo DHCP Discover → relay → Offer em redes segmentadas por VLAN
- Diferença entre switching L2 (intra-VLAN) e roteamento L3 (inter-VLAN/WAN)
- Documentação técnica em LaTeX com tabelas de endereçamento, topologia e análise de riscos

## Referências do relatório

- Kurose, J. F.; Ross, K. W. — *Computer Networking: A Top-Down Approach*
- RFC 2328 — OSPF Version 2
- RFC 1542 — DHCP Relay Agent (ip helper-address)
- IEEE 802.1Q — Virtual LANs
