# Atividade de Laboratório — Configuração de Serviços de Rede em uma LAN

## Objetivo

O objetivo desta atividade é projetar e configurar uma rede local (LAN) com serviços básicos de rede, como **DHCP**, **DNS**, **HTTP** e **Wi-Fi**, permitindo a comunicação entre diferentes dispositivos.

---

## Cenário

Uma pequena rede local será implementada para atender dispositivos cabeados e sem fio. A rede contará com um servidor central responsável por oferecer serviços de rede e por permitir o acesso a uma página web interna.

### Topologia da Rede
- **1 Servidor**
- **1 Switch**
- **1 Access Point**
- **3 Hosts:**
  - 1 Desktop (conectado via cabo)
  - 1 Laptop (conectado via Wi-Fi)
  - 1 Smartphone (conectado via Wi-Fi)

O servidor deverá possuir o endereço IP `192.168.1.2` e fornecer os seguintes serviços:
- **DHCP:** para atribuição automática de endereços IP aos dispositivos da rede
- **DNS:** para resolução de nomes
- **HTTP:** para hospedagem de uma página web interna

A figura apresentada em aula mostra a topologia lógica da rede a ser implementada.

---

## Tarefas

Os alunos deverão realizar as seguintes etapas no **Cisco Packet Tracer**:

### 1. Montagem da Topologia
- Inserir os dispositivos necessários:
  - 1 Server
  - 1 Switch
  - 1 Access Point
  - 1 PC
  - 1 Laptop
  - 1 Smartphone
- Realizar as conexões físicas adequadas entre os dispositivos.

### 2. Configuração do Servidor
- Configurar o endereço IP do servidor como:
  - **IP:** `192.168.1.2`
  - **Máscara de sub-rede:** `255.255.255.0`
- Ativar e configurar os serviços: **DHCP**, **DNS** e **HTTP**.

### 3. Configuração do DHCP
- Criar um pool DHCP para a rede `192.168.1.0/24`.
- Definir:
  - Gateway da rede
  - DNS apontando para o próprio servidor (`192.168.1.2`)
  - Intervalo de endereços para os hosts

### 4. Configuração do DNS
- Criar um registro DNS para um site interno, por exemplo: `www.rede.local`.
- O nome deverá apontar para o endereço IP do servidor (`192.168.1.2`).

### 5. Configuração do HTTP
- Ativar o serviço HTTP no servidor.
- Criar uma página simples contendo uma mensagem de teste (por exemplo: *"Servidor Web funcionando"*).

### 6. Configuração da Rede Sem Fio
- Configurar o Access Point com:
  - Nome da rede (SSID)
  - Segurança (opcional)
- Conectar:
  - Laptop
  - Smartphone
- Ambos devem obter endereço IP via DHCP.

### 7. Configuração dos Hosts
- O PC, o laptop e o smartphone devem obter endereço IP automaticamente via DHCP.

### 8. Testes de Conectividade
- Verificar:
  - Ping entre os dispositivos
  - Resolução de nome via DNS
  - Acesso ao site utilizando o navegador web
