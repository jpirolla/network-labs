# Projeto de Aula — Roteamento com OSPF Multiárea

## Objetivo

Implementar uma rede utilizando o protocolo de roteamento **OSPF com múltiplas áreas**, permitindo a comunicação entre diferentes segmentos de rede e a centralização do serviço de **DHCP**.

---

## Parte 1 — Topologia Inicial

1. **Elaboração da Topologia:**
   - Montar a topologia conforme a figura fornecida.

2. **Configuração OSPF Multiárea:**
   - Configurar o protocolo OSPF utilizando três áreas:
     - **Área 0** (Backbone)
     - **Área 1**
     - **Área 2**

3. **Endereçamento e Conectividade:**
   - Configurar os endereçamentos IP conforme indicado na topologia.
   - Garantir a conectividade completa (ping) entre todas as redes da topologia.

4. **Validação CLI do OSPF:**
   - Validar o funcionamento do OSPF utilizando os seguintes comandos de verificação Cisco IOS:
     ```cisco
     show ip ospf neighbor
     show ip ospf interface
     show ip ospf database
     show ip route
     ```

5. **Servidor Centralizado (DHCP / DNS / Web):**
   - O servidor da rede `192.168.1.0/24` deverá possuir o IP `192.168.1.2` e atuar como servidor DHCP e DNS.
   - A rede `192.168.2.0/24` deverá obter endereçamento IP automaticamente via DHCP a partir de `192.168.1.2`.
   - Configurar **DHCP Relay** (`ip helper-address`) nos roteadores necessários para encaminhar solicitações DHCP entre redes distintas.
   - Validar o acesso ao servidor Web (`192.168.1.2`) e a resolução de nomes via servidor DNS (`192.168.1.66`).

---

## Parte 2 — Expansão da Rede (Desafio)

Para os alunos que concluírem a implementação da topologia inicial, deverá ser realizada uma expansão da rede com os seguintes requisitos:

1. **Novas Redes:**
   - Adicionar duas novas redes à topologia:
     - Uma nova rede conectada ao **Router3** (Área 3)
     - Uma nova rede conectada ao **Router2** (Área 4)

2. **Configuração das Áreas 3 e 4:**
   - As novas áreas deverão se comunicar corretamente com todas as demais áreas por meio da Área 0 (Backbone).

3. **DHCP Centralizado nas Novas Áreas:**
   - Todas as novas redes deverão obter endereçamento IP automaticamente a partir do servidor DHCP centralizado (`192.168.1.2`).
   - Configurar os roteadores ABR para permitir o encaminhamento de mensagens DHCP entre as áreas.

---

## Criterios de Sucesso
- Comunicação de ponta a ponta entre todas as sub-redes;
- Propagação correta das rotas OSPF (rotas intra-área e inter-área `O IA`);
- Obtenção automática de IP via DHCP em todas as áreas;
- Acesso aos serviços DHCP/DNS/Web a partir de qualquer host da topologia.

---

## Material de Apoio
- Vídeo auxiliar: [http://bit.ly/43QIWnQ](http://bit.ly/43QIWnQ)
