# Multiplexação e Demultiplexação na camada de Transporte

## Overview

Este projeto tem como objetivo demonstrar, de forma prática, os conceitos de multiplexação e demultiplexação na camada de transporte, com base no modelo TCP/IP.

A implementação consiste em uma aplicação cliente-servidor capaz de gerar múltiplos fluxos de comunicação simultâneos e evidenciar como esses fluxos são tratados no destino. Embora o controle real dessas operações seja realizado pelo kernel do sistema operacional, o projeto busca tornar esse comportamento observável no nível da aplicação.

Além disso, foram integradas ferramentas de observabilidade para coleta e visualização de métricas em tempo real, permitindo analisar o comportamento das conexões e o fluxo de dados.

### Principais aspectos abordados

* Geração de múltiplos fluxos de comunicação a partir de um único host
* Identificação de conexões por meio da tupla (IP origem, porta origem, IP destino, porta destino)
* Uso de portas efêmeras para diferenciação de conexões
* Concorrência no cliente por meio de múltiplas threads
* Multiplexação de I/O no servidor utilizando `select()`
* Monitoramento de métricas com Prometheus
* Visualização de dados com Grafana

### Painéis (Métricas e Resultados)

A instrumentação do projeto reflete o comportamento do tráfego através de cinco perspectivas distintas de observabilidade:

1. **Demultiplexação (Raio-X de Sockets):** Este painel de linha do tempo (*State-Timeline*) mapeia o ciclo de vida de cada conexão TCP. Os marcadores de ativação/desativação representam portas efêmeras geradas pelo host do cliente. A métrica comprova visualmente, na **Camada de Aplicação**, o resultado da demultiplexação feita pelo Sistema Operacional subjacente: o servidor Python (`server.py`) gerencia ativamente as dezenas de conexões abertas usando I/O Multiplexing, isolando corretamente o conteúdo oriundo do mesmo IP, suportado pelo mapeamento via tuplas (IP:porta).
2. **Carga Total (Multiplexação Agregada):** Exibe o número total de conexões simultaneamente ativas (métrica `sum`). Este painel materializa o conceito físico de multiplexação de rede: dezenas de sessões geradas por variadas *threads* independentes que compartilham concorrentemente a mesma placa de rede (ou interface de loopback) para o transporte das mensagens.
3. **Throughput de Mensagens por Fluxo Isolado:** Detalha a taxa de recebimento (mensagens/segundo usando `rate() > 0`) segmentada estritamente pela tupla de origem. A visualização confirma o sucesso da separação de contextos pelo TCP, onde rajadas de comunicação (*bursts*) de diferentes fluxos não sofrem colisão (*crosstalk*) na Camada de Aplicação. Filtros dinâmicos garantem o rastreio apenas de *sockets* em atividade perante o processo.
4. **Largura de Banda (Throughput em bytes/s):** Ilustra o escoamento global de tráfego. Enquanto o Painel 3 foca no comportamento lógico independente ditado pelo TCP, este painel mede a utilização bruta no enlace físico da rede originada do tráfego originado por processos concorrentes.
5. **Latência de Processamento (Gargalo de I/O e Clock Skew):** Aferida através de uma relação matemática de recebimento e *timestamps* de pacotes, este painel aprova a eficiência no processamento via um laço não bloqueante (`select()`), lidando com as requisições geradas. Adicionalmente, atua como termômetro de *Clock Skew*. Sob condições distribuídas assíncronas, flutuações e latências sub-zero ilustram a complexidade acadêmica da dessincronização inofensiva de relógios de hardware (RTC) no ecossistema de infraestrutura de containers.

## Sumário

* [Estrutura do projeto](#estrutura-do-projeto)
* [Arquitetura](#arquitetura)
* [Camada de Transporte](#camada-de-transporte)

  * [Multiplexação](#multiplexação)
  * [Demultiplexação](#demultiplexação)
* [I/O Multiplexing com select()](#io-multiplexing-com-select)
* [Ciclo de vida de uma conexão](#ciclo-de-vida-de-uma-conexão)
* [Observabilidade com Prometheus](#observabilidade-com-prometheus)
* [Visualização no Grafana](#visualização-no-grafana)
* [Resumo das entidades](#resumo-das-entidades)
* [Referências](#referências)



## Estrutura do projeto 

``` bash
transport-mux-lab/
├── docker-compose.yml              # orquestra a infra
├── server/
│   ├── Dockerfile                  
│   ├── requirements.txt            # dependências Python do servidor
│   └── server.py                   # O núcleo: select() + demultiplexação
├── client/
│   ├── Dockerfile                  
│   └── client.py                   # O multiplexador (usei threads nessa versao)
├── prometheus/
│   └── prometheus.yml              # config do coletor de métricas
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── datasource.yml      # vinculação automática do Grafana ao Prometheus
    │   └── dashboards/
    │       └── dashboards.yml      # aponta os dashboards que o Grafana deve carregar
    └── dashboards/
        └── multiplex_dashboard.json # os 5 painéis de observabilidade
```

## Arquitetura
Dado esse contexto, pensei em implementar uma comunicação cliente-servidor que pudesse tornar visível o comportamento da camada de transporte, ou seja, evidenciar a existência de múltiplos fluxos sendo tratados simultaneamente.

É importante destacar que o projeto não implementa o TCP em si, mas sim simula, no nível da aplicação, a separação de fluxos, já que o gerenciamento real (incluindo multiplexação e demultiplexação) é feito pelo kernel do sistema operacional.

Inicialmente, desenvolvi a camada de cliente e servidor e, posteriormente, incorporei ferramentas de observabilidade (Prometheus e Grafana) para monitorar e visualizar o comportamento da aplicação em tempo real.

- Cliente -> gera múltiplos fluxos simultâneos (multiplexação)
- Servidor -> recebe e separa os fluxos (demultiplexação)
- Prometheus -> coleta métricas do servidor
- Grafana -> visualiza essas métricas

## Camada de Transporte
A camada de transporte (TCP/UDP) tem como responsabilidade a comunicação entre os processos e a entrega de dados (TCP) e identificação de origem e destino dos dados através do ip (identificando o host) e a porta (identificando o processo via socket). 
Em resumo, temos a camada de rede entregando dados entre hosts 
e a camada de transporte entregando dados entre processos dentro desses hosts.

Assim, a comunicação é identificada por:
```
(IP origem, porta origem, IP destino, porta destino)
```

### Multiplexação

Em linhas gerais, multiplexação é o processo realizado no host de origem, onde a camada de transporte coleta dados de diferentes sockets (processos), encapsula esses dados em segmentos e os envia através da camada de rede.

No contexto do projeto, isso acontece no cliente:

- Múltiplas threads representam múltiplos processos lógicos
- Cada thread cria um socket TCP
- Cada socket envia dados independentemente

Apesar disso, todos esses fluxos compartilham o mesmo IP, utilizam a mesma interface de rede e passam pela mesma pilha TCP/IP, caracterizando a multiplexação.

#### Infraestrutura de rede 
Nesse projeto, dado que utilizei o docker, a rede em questão é representada pela Docker bridge network, que consiste em uma rede local virtual criada pelo Docker para permitir comunicação entre containers (docker cria uma interface virtual no host, tal como um switch virtual, e cada container ganha uma interface de rede virtual e um ip dentro da rede. o bridge conecta ambos tal como um switch de rede). 

Mesmo compartilhando a mesma infraestrutura de rede, os fluxos são diferenciados por suas portas:

```
IP:Porta origem  | IP:Porta destino
172.18.0.5:36230 | 172.18.0.3:5000
172.18.0.5:36232 | 172.18.0.3:5000
```
Cada conexão TCP recebe uma porta efêmera, atribuída automaticamente pelo sistema operacional.


#### Threads para geração de concorrência
Geração de concorrência (Threads)

No projeto, utilizei múltiplas threads no cliente como forma de simular múltiplos processos de aplicação ativos simultaneamente.Assim, cada thread **cria seu próprio socket TCP, estabelece uma conexão independente com o servidor e envia mensagens de forma assíncrona em relação às demais**.

Apesar de, conceitualmente, a multiplexação envolver processos distintos, o uso de threads aqui cumpre o mesmo papel prático de gerar múltiplos fluxos concorrentes saindo de um mesmo host. Embora a teoria trate de processos independentes, na prática, threads dentro de um mesmo processo também são capazes de gerar múltiplos fluxos de comunicação, já que cada socket criado é gerenciado independentemente pelo sistema operacional (pois quando fazemos socket.socket(...) criamos uma struct socket que é associada a um file descriptor que registra isso na tabela de processos). 

A ideia seria manter
- cada thread representando um fluxo lógico independente que chamam socket()
- cada socket representando um endpoint de comunicação
- cada conexão recebendo uma porta efêmera distinta

Assim, mesmo dentro de um único processo (o programa cliente), conseguimos simular o comportamento descrito na teoria, onde múltiplas aplicações compartilham a mesma infraestrutura de rede.

### Demultiplexação
Demultiplexação é o processo realizado no host de destino, onde a camada de transporte recebe segmentos da camada de rede e entrega os dados ao socket correto.

Note que a entrega não é feita diretamente ao processo, mas ao socket associado ao processo.

Cada socket possui um identificador único, que depende do protocolo


#### TCP 
Um socket TCP é identificado por uma tupla de quatro elementos:
```
(IP origem, porta origem, IP destino, porta destino)
```

Isso significa que conexões diferentes (mesmo que para o mesmo servidor) são tratadas separadamente e o servidor pode manter múltiplas conexões simultâneas

No server.py, representamos esse processo no trecho 

```python
clients[client_socket] = client_address
addr = clients[sock]
```
Aqui, associamos cada socket a um cliente.

Contudo, é importante reforçar que o **kernel já realizou a demultiplexação real dos segmentos TCP para sockets** antes da aplicação acessar os dados.

Ou seja, o recv() já recebe dados do socket correto e a aplicação apenas organiza/rotula esses dados


## I/O Multiplexing com select()

Além da multiplexação da camada de transporte, o servidor utiliza I/O multiplexing que permite que um único processo monitore múltiplos sockets simultaneamente.

Sem isso, o servidor teria que bloquear em um único socket ou criar uma thread por conexão

O select() resolve esse problema perguntando ao sistema operacional “quais sockets possuem dados disponíveis para leitura?”

Assim, o servidor consegue atender múltiplas conexões concorrentes com um único fluxo de execução

```
ready_to_read, _, _ = select.select(sockets_monitorados, [], [], 1.0)
```

## Ciclo de vida de uma conexão
Cada conexão segue o fluxo:

- Cliente chama connect()
- Servidor executa accept()
- Socket é criado e registrado
- Cliente envia mensagens
- Servidor recebe via recv()
- Servidor responde (ACK)
- Cliente encerra conexão
- Servidor detecta recv() == vazio
- Conexão é removida


## Observabilidade com Prometheus

Além da visualização das conexões no terminal, a ideia foi medir o comportamento da aplicação e torná-lo explicitamente observável. Para isso, utilizei Prometheus e Grafana, que são ferramentas amplamente utilizadas no mercado para monitoramento de sistemas distribuídos. 

### Tipos de métricas utilizadas

#### Gauge (estado)
- ACTIVE_CONNECTIONS: representa as conexões ativas no momento

#### Counter (eventos)
- MESSAGES_RECEIVED: representa o número de mensagens recebidas
- BYTES_RECEIVED: representa o número de bytes recebidos


#### Histogram (distribuição)
- PROCESSING_LATENCY: representa o tempo entre envio e recebimento

A ideia era conseguir responder perguntas como:

* Quantas conexões simultâneas existem?
* Qual fluxo está mais ativo?
* Qual a taxa de mensagens?
* Existe gargalo?
* A latência está aumentando?


## Visualização no Grafana
(colocar prints)
O dashboard foi estruturado em 5 painéis descritos a seguir

### 1. Demultiplexação visual (state timeline)
Cada linha representa:
```
IP:porta
```

Mostra:
* nascimento da conexão
* duração
* encerramento
Tal painel é a representação direta da demultiplexação

### 2. Carga total
```
sum(active_connections)
```
Mostra quantas conexões simultâneas existem, fornecendo uma visão agregada da multiplexação

### 3. Throughput por fluxo
```
rate(messages_received_total)
```
Mostrando a atividade individual de cada conexão

### 4. Largura de banda
```
rate(bytes_received_total)
```

Mostra  volume total de dados

### 5. Latência
```
rate(sum) / rate(count)
```
Mostra o tempo médio de processamento


## Resumo das entidades
Em resumo, o fluxo de acontecimentos do projeto se divide nas entidades descritas a seguir. 

### No cliente
* Threads geram concorrência
* Cada conexão usa uma porta efêmera
* O sistema operacional gerencia envio

### Na rede
* Pacotes são roteados pelo IP
* TCP garante entrega e ordem


### No servidor
* `select()` faz multiplexação de I/O
* sockets representam conexões
* dados são separados por origem



---
## Referências

- Kurose, J. F.; Ross, K. W.  
  *Computer Networking: A Top-Down Approach* — Capítulo 3.2 (Multiplexação e Demultiplexação)

- Python Software Foundation  
  [socket — Low-level networking interface](https://docs.python.org/3/library/socket.html#socket.socket.accept)