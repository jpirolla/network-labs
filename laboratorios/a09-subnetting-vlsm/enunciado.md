# Implementação de Subnets VLSM (62, 30 e 2 Hosts)

## Especificação

Considere a rede `192.168.1.0/24`.

Divida essa rede em **5 sub-redes**, de forma a atender às seguintes necessidades de capacidade:
- **3 sub-redes com 62 hosts cada**
- **1 sub-rede com 30 hosts**
- **1 sub-rede com 2 hosts** (link ponto a ponto)

---

## Regras de Alocação

As sub-redes devem obrigatoriamente:
- Pertencer ao bloco original `192.168.1.0/24`
- Não apresentar sobreposição de endereços
- Ser compatíveis com **VLSM** (*Variable Length Subnet Mask*)
- Seguir a ordem e alocação conforme indicado no diagrama de topologia

---

## Requisitos de Informação por Sub-rede

Para cada uma das 5 sub-redes, especifique:
1. **Identificador da Sub-rede**
2. **Notação CIDR** (ex: `/26`, `/27`, `/30`)
3. **Endereço de Rede** (Network Address)
4. **Máscara de Sub-rede** (Decimal Ponto)
5. **Faixa de Hosts Válidos** (Primeiro e último IP utilizáveis)
