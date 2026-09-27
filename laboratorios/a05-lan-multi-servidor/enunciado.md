# Prática II (Continuação) — Protocolos Web, Arquiteturas e Fundamentos de Redes

**Instituto de Ciências Matemáticas e de Computação — ICMC/USP**  
**Disciplina:** SSC0540 — Redes de Computadores  
**Professor:** Prof. Jó Ueyama  

---

## Observações
- As respostas deste exercício devem ser submetidas até o final da aula.
- Submeter as respostas até o ponto que você conseguiu resolver.
- A submissão deve ser feita exclusivamente pela plataforma Moodle.
- Esta atividade é individual.

---

## Parte 1 — HTTP, HTTPS e Web

### Exercício 1 — Requisição HTTPS Manual (Porta 443)
Execute o comando:
```bash
echo -e "GET / HTTP/1.1\r\nHost: www.uol.com.br\r\nConnection: close\r\n\r\n" | openssl s_client -connect www.uol.com.br:443 -quiet
```
**Perguntas:**
- O conteúdo retornado é legível?
- Por que precisamos do `openssl s_client` em vez do `nc`?
- Qual a principal diferença entre HTTP e HTTPS?

---

### Exercício 2 — Interpretação de Códigos HTTP
**Perguntas:**
- Qual o significado de:
  - `200 OK`
  - `404 Not Found`
- Em que situações cada um ocorre?
- O `curl` mostra o corpo da resposta nesses casos?

---

### Exercício 3 — Verificação de Modificação da Página (Wikipedia)
Execute o comando:
```bash
curl -I https://www.wikipedia.org
```
**Perguntas:**
- A página foi trazida do servidor hoje?
- Qual é o valor do campo `Last-Modified`?
- A página parece recente?

---

### Exercício 4 — Requisição Condicional com `If-Modified-Since`
Execute o comando:
```bash
curl -I -H "If-Modified-Since: Sat, 14 Mar 2026 15:00:00 GMT" https://www.wikipedia.org
```
**Perguntas:**
- O servidor retornou `HTTP/2 304 Not Modified` ou `200 OK`?
- O que isso indica sobre a página?

---

### Exercício 5 — Interpretação do GET Condicional
**Perguntas:**
- O que significa `HTTP/2 304 Not Modified`?
- Em que situação o cliente evita baixar o conteúdo?
- Qual a vantagem disso em termos de desempenho e uso de rede?

---

## Parte 2 — Arquiteturas de Rede e Distribuição

### Exercício 6 — Peer-to-Peer (P2P)
**Perguntas:**
- Por que o tempo para distribuição de conteúdo não cresce linearmente em redes P2P?
- Considerando que $N$ é o número de hospedeiros, explique o comportamento do tempo no gráfico.
- Por que, no modelo cliente-servidor, o tempo cresce de forma mais limitada/constante em comparação ao P2P para pequenas escalas?

---

## Parte 3 — Fundamentos de Redes

### Exercício 7 — Comutação de Circuitos
**Pergunta:**
- Quantas conexões podem ser implementadas em um sistema com $f$ canais e $t$ slots?

---

### Exercício 8 — Tipos de Redes para Aplicações
**Perguntas:**
- A transmissão de um vídeo do YouTube funciona melhor em:
  - Rede de circuitos virtuais ou
  - Rede de datagramas?
- E a transmissão de um arquivo via FTP? Justifique.

---

### Exercício 9 — Modelo OSI
**Perguntas:**
- Qual outra rede (além da Internet) segue o modelo OSI?
- Desenhe ou especifique a pilha de protocolos dessa rede.

---

### Exercício 10 — Arquitetura em Camadas
**Perguntas:**
- Por que redes de computadores são organizadas em camadas?
- O que se ganha com isso?
- O que se perde com isso?

---

### Exercício 11 — Núcleo vs. Periferia da Rede
**Perguntas:**
- Onde geralmente se concentra a maior parte do software da rede: no núcleo ou na periferia?
- Por quê?

---

### Exercício 12 — Evolução de Tecnologias de Rede
**Pergunta:**
- Por que tecnologias como ATM (*Asynchronous Transfer Mode*) e WiMAX deixaram de ser amplamente utilizadas?
