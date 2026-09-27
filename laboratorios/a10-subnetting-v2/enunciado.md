# Subnetting com VLSM v2 — Prática Packet Tracer

## Especificação

Considere a rede base `192.168.1.0/24`.

Divida essa rede em **5 sub-redes** com máscaras variáveis (VLSM), atendendo aos seguintes requisitos de dimensionamento:
- **3 sub-redes para 62 hosts**
- **1 sub-rede para 30 hosts**
- **1 sub-rede para 2 hosts** (ponto a ponto entre roteadores)

---

## Regras de Configuração

- Todas as sub-redes devem estar contidas no bloco `192.168.1.0/24`.
- Não deve haver sobreposição de IPs.
- Aplicar as configurações no **Cisco Packet Tracer** (arquivos `.pkt`).

---

## Tabela de Cálculo Solicitada

Para cada sub-rede calculada, determine:
- **Nome/Identificação da Sub-rede**
- **Notação CIDR**
- **Endereço de Rede**
- **Máscara de Sub-rede**
- **Faixa de IPs Utilizáveis (Hosts Válidos)**
