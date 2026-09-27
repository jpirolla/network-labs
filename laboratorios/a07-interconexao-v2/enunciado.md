# Interconexão de Redes Usando Roteadores — Especificação de Projeto de Rede

## 1. Objetivo

Projetar e implementar uma infraestrutura de rede composta por duas sub-redes distintas, interligadas por um backbone de alta velocidade, com serviços distribuídos entre servidores dedicados, conforme ilustrado na figura fornecida.

---

## 2. Topologia Geral

- **Duas redes locais independentes:**
  - **Rede 1 (lado esquerdo):** `192.168.1.0/24`
  - **Rede 2 (lado direito):** `192.168.2.0/24`
- **Interconexão:** Realizada por um roteador central.
- **Switches:** Cada rede conectada a um switch local.
- **Backbone:** Conexão entre roteador e switches utilizando **fibra óptica**.

---

## 3. Componentes da Rede

### Rede `192.168.1.0/24` (Lado Esquerdo)
- 1 Switch
- 2 Servidores:
  - **Servidor 1:** DHCP, Web e E-mail (*Atenção: o servidor DHCP é único e serve para as duas redes*)
  - **Servidor 2:** Reservado para expansão ou redundância
- Hosts (clientes)

### Rede `192.168.2.0/24` (Lado Direito)
- 1 Switch
- 2 Servidores:
  - **Servidor 1:** DNS (dedicado)
  - **Servidor 2:** Reservado para expansão ou redundância
- Hosts (clientes)

### Interconexão
- 1 Roteador central com interfaces para ambas as redes.
- Conexão com switches via fibra óptica, conforme a topologia.

---

## 4. Endereçamento IP

### Rede `192.168.1.0/24`
- **Gateway:** `192.168.1.1`
- **Servidor DHCP/Web/Mail:** `192.168.1.10`
- **Servidor Adicional:** `192.168.1.11`
- **Faixa DHCP (exemplo):** `192.168.1.100` – `192.168.1.200`

### Rede `192.168.2.0/24`
- **Gateway:** `192.168.2.1`
- **Servidor DNS:** `192.168.2.10`
- **Servidor Adicional:** `192.168.2.11`

---

## 5. Serviços de Rede

- **Servidor DNS (Rede `192.168.2.0/24`):** Responsável pela resolução de nomes para ambas as redes.
- **Servidor DHCP (Rede `192.168.1.0/24`):** Distribuição automática de endereços IP para ambas as redes mediante configuração de *relay*.
- **Servidor Web (Rede `192.168.1.0/24`):** Hospedagem de aplicações e páginas internas.
- **Servidor de E-mail (Rede `192.168.1.0/24`):** Gerenciamento de envio e recebimento de mensagens.

---

## 6. Backbone e Infraestrutura

- Comunicação entre roteador e switches por **fibra óptica**, conforme a topologia apresentada.
- Utilização de interfaces Gigabit Ethernet (1 Gbps) ou superiores.
- Foco em desempenho, baixa latência e maior capacidade de tráfego.

---

## 7. Roteamento

- Roteador com duas interfaces:
  - Uma conectada à rede `192.168.1.0/24`
  - Outra conectada à rede `192.168.2.0/24`
- Responsável pelo roteamento de pacotes entre as redes.
- Configuração de **DHCP relay** para atender à rede `192.168.2.0/24`.
