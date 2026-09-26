# A11 — Protocolos de Roteamento: RIP, OSPF e BGP

**Disciplina:** SSC0540 — Redes de Computadores | **Tipo:** Atividade escrita (questionário + resolução em PDF)

## Objetivo

Responder questões conceituais sobre os três principais protocolos de roteamento estudados na disciplina: **RIP**, **OSPF** e **BGP**, com base em videoaula e slides.

## Questões abordadas

1. Quais protocolos de roteamento são apresentados na aula?
2. O que é o RIP e qual métrica ele utiliza?
3. Como funcionam os anúncios no RIP?
4. O que é o OSPF?
5. Quais são alguns recursos avançados do OSPF?
6. Qual é a função do BGP na Internet?

## Conceitos estudados (conforme resolução)

### RIP (Routing Information Protocol)
- Protocolo de **vetor de distância**
- Métrica: número de saltos (hops), máximo 15
- Atualizações periódicas a cada 30/90/180 segundos (UDP)
- Processo `routed` em nível de aplicação

### OSPF (Open Shortest Path First)
- Protocolo de **estado de enlace** (link-state)
- Algoritmo de **Dijkstra** para cálculo de menor custo
- Mensagens transportadas diretamente sobre IP
- Recursos avançados: autenticação, balanceamento de carga, estrutura hierárquica multi-área, suporte unicast/multicast

### BGP (Border Gateway Protocol)
- Protocolo de roteamento entre **Sistemas Autônomos (AS)**
- Sessões **eBGP** (externas) e **iBGP** (internas)
- Funções: acessibilidade de redes, propagação de rotas, políticas de roteamento

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `enunciado.txt` | Questões da atividade |
| `resolucao.txt` | Resolução escrita das 6 questões |
| `slides-aula.pdf` | Slides da aula sobre RIP, OSPF e BGP |
