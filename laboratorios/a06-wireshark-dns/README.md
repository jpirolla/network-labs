# A06 — Análise do Protocolo DNS com Wireshark

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Laboratório (Wireshark)

## Objetivo

Capturar e analisar pacotes DNS em tráfego real usando o Wireshark, compreendendo como funciona a resolução de nomes no nível do protocolo.

## Conceitos praticados

### Protocolo DNS
- Estrutura de mensagens DNS (query e response)
- Tipos de registros: A, AAAA, NS, MX
- Transporte sobre **UDP** (porta 53)
- Cache DNS no sistema operacional

### Ferramentas de diagnóstico utilizadas
- **`nslookup`** — consulta de registros DNS a servidores específicos
  - Sintaxe: `nslookup [-option] host-to-find [dns-server]`
  - Consulta de servidor autoritativo de universidades
  - Consulta de MX records
- **`ipconfig /displaydns`** — visualização do cache DNS local
- **`ipconfig /flushdns`** — limpeza do cache DNS

### Análise no Wireshark
- Filtro: `ip.addr == <seu_IP>`
- Identificação de query e response DNS
- Porta destino da query: UDP/53
- Comparação entre DNS padrão e DNS autoritativo
- Verificação se IP do SYN subsequente corresponde ao DNS response

## Relação com redes e troubleshooting

A análise de pacotes DNS com Wireshark é uma técnica fundamental para:
- Diagnosticar problemas de resolução de nomes
- Verificar qual servidor DNS está sendo consultado
- Identificar respostas incorretas ou ausentes
- Entender o fluxo completo de uma requisição HTTP (DNS → TCP SYN → HTTP GET)

## Ferramentas

- Wireshark
- nslookup

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.txt` | Especificação da atividade (perguntas sobre pacotes DNS) |
| `roteiro-wireshark.txt` | Roteiro completo do Wireshark DNS Lab (inclui questões e metodologia) |
| `Wireshark_DNS_v8.0-2.pdf` | Material oficial do Wireshark DNS Lab (v8.0) |
