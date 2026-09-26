# Projeto 2 — Rede Corporativa Kodalabs: Expansão WAN, OSPF Multi-área e IoT

**Disciplina:** SSC0540 — Redes de Computadores | ICMC/USP  
**Professor:** Jó Ueyama  
**Tipo:** Projeto acadêmico completo — evolução do Projeto 1

---

## Objetivo

Expandir a infraestrutura da Kodalabs introduzindo três novos elementos:

1. **OSPF multi-área** (Área 0, 1 e 2) substituindo área única
2. **Data Center compartilhado** (cloud privada) — infraestrutura neutra acessível por ambas as filiais
3. **Internet das Coisas (IoT)** — dispositivos IoT em cada localidade

## Arquitetura

```
[Área 1 — Campinas]          [Área 0 — Backbone]          [Área 2 — São Carlos]
   R-CPN-01 (ABR) ────────── R-DC-CLOUD ────────── R-SCA-01 (ABR)
   VLANs 10–50                Data Center              VLANs 60–90
   192.168.10.0/24            192.168.100.0/29         192.168.60.0/24
```

## Conceitos praticados

### OSPF Multi-área
- **3 áreas OSPF**: Área 0 (backbone), Área 1 (Campinas), Área 2 (São Carlos)
- **ABR** (Area Border Router): `R-CPN-01` e `R-SCA-01` interconectam as áreas ao backbone
- `R-DC-CLOUD` opera exclusivamente na Área 0 (não é ABR)
- **LSDB** (Link-State Database) — banco de dados de topologia por área
- Redução da complexidade do LSDB no Data Center via rotas resumidas

### Data Center Privado
- Serviços centralizados: HTTP, FTP, SMTP, DNS, DHCP, IoT
- Sub-rede `192.168.100.0/29` (servidor) + bloco interno `10.0.0.1/24`
- DHCP do Data Center atende ambas as filiais via relay

### VLANs e Segmentação
- Mantém a segmentação do Projeto 1 (9 VLANs departamentais)
- Justificativas aprofundadas por departamento:
  - Engenharia/Data Science: isolamento de tráfego ETL/ML
  - TI: proteção de acesso SSH e ferramentas de monitoramento
  - Servidores: princípio de least privilege na camada de rede (LGPD)
  - Visitantes: isolamento total de dispositivos não confiáveis

### Endereçamento
- Separação geográfica por bloco: `192.168.10.x` = Campinas, `192.168.60.x` = São Carlos
- Semântica geográfica nas tabelas de roteamento e ACLs

## Como visualizar

Abra o arquivo `projeto2.pkt` no **Cisco Packet Tracer** (versão 8.x recomendada).

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `projeto2.pkt` | Implementação completa no Cisco Packet Tracer |
| `relatorio.pdf` | Relatório técnico compilado (LaTeX) |
| `main.tex` | Fonte LaTeX do relatório principal |
| `justificativas.tex` | Módulo LaTeX com justificativas de segmentação por VLAN |
| `link_gravacao.txt` | Link para vídeo de apresentação |

## Progressão em relação ao Projeto 1

| Aspecto | Projeto 1 | Projeto 2 |
|---------|-----------|-----------|
| OSPF | Área 0 única | Multi-área (0, 1, 2) com ABR |
| Serviços | Servidor na matriz (Campinas) | Data Center neutro (cloud privada) |
| IoT | Não | Sim — dispositivos IoT por localidade |
| DHCP | Servidor em Campinas | Centralizado no Data Center |
| Roteamento | 2 roteadores | 3 roteadores (ABR + DC) |

## Aprendizados

- Diferença prática entre OSPF área única e multi-área (escalabilidade, LSDB, ABR)
- Neutralidade arquitetural do Data Center como infraestrutura compartilhada
- Integração de IoT em topologias de rede corporativa com segmentação
- Justificativa de segmentação por VLAN sob perspectiva de segurança e LGPD

## Referências do relatório

- Kurose, J. F.; Ross, K. W. — *Computer Networking: A Top-Down Approach*
- RFC 2328 — OSPF Version 2
- RFC 1542 — Clarifications and Extensions for the Bootstrap Protocol
- IEEE 802.1Q — Virtual LANs
