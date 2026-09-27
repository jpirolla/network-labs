# A01 — Configuração de Serviços de Rede em uma LAN

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Laboratório (Cisco Packet Tracer)

## Objetivo

Projetar e configurar uma rede local (LAN) com serviços básicos de rede, permitindo comunicação entre dispositivos cabeados e sem fio.

## Cenário

Topologia composta por: 1 Servidor, 1 Switch, 1 Access Point, 1 PC (cabo), 1 Laptop (Wi-Fi) e 1 Smartphone (Wi-Fi).

O servidor (IP fixo `192.168.1.2`) centraliza os serviços: **DHCP**, **DNS** e **HTTP**.

## Conceitos praticados

- Configuração de endereçamento IP estático (servidor) e dinâmico (clientes via DHCP)
- Serviço **DHCP**: pool de endereços, gateway e DNS distribuídos automaticamente
- Serviço **DNS**: registro `www.rede.local` apontando para o servidor
- Serviço **HTTP**: página web interna com mensagem de teste
- Rede sem fio: configuração de Access Point (SSID, segurança)
- Testes de conectividade: `ping` entre dispositivos, acesso via navegador, resolução de nomes

## Ferramentas

- Cisco Packet Tracer

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.md` | Especificação completa da atividade |
| `lab1_dns_http_dhcp.pkt` | Implementação no Cisco Packet Tracer |
