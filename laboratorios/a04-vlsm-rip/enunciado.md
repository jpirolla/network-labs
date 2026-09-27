# Prática II — Exploração de Protocolos HTTP, HTTPS, Sockets e P2P

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

## Exercícios

### Exercício 1 — Inspecionando Cabeçalhos HTTP
Execute o comando:
```bash
curl -I -v https://www.icmc.usp.br
```
**Perguntas:**
- Qual versão do HTTP foi utilizada (`HTTP/1.1` ou `HTTP/2`)?
- O servidor retornou `200 OK`?

---

### Exercício 2 — Comparação HTTP/1.1 vs HTTP/2
Execute os comandos:
```bash
curl --http1.1 -w "HTTP1.1: %{time_total}s\n" -o /dev/null -s https://www.google.com
curl --http2 -w "HTTP2: %{time_total}s\n" -o /dev/null -s https://www.google.com
```
**Perguntas:**
- Qual versão foi mais rápida?
- A diferença foi significativa?
- Por que o `HTTP/2` tende a ser mais eficiente?

---

### Exercício 3 — Testando Múltiplas Requisições
Execute os comandos:
```bash
curl --http1.1 -o /dev/null -s -w "HTTP/1.1 Time: %{time_total}s\n" https://www.google.com https://www.google.com
curl --http2 -o /dev/null -s -w "HTTP/2 Time: %{time_total}s\n" https://www.google.com https://www.google.com
```
**Perguntas:**
- Qual protocolo apresentou melhor desempenho com múltiplas requisições?
- Como isso se relaciona com multiplexação?
- Por que o `HTTP/1.1` pode sofrer com *Head-of-Line Blocking* (HOL)?

---

### Exercício 4 — Criando e Armazenando Cookies
Execute o comando:
```bash
curl -i -c cookies.txt "https://httpbin.org/response-headers?Set-Cookie=usuario=joao"
```
**Perguntas:**
- Qual header HTTP é retornado pelo servidor?
- O que foi armazenado no arquivo `cookies.txt`?

---

### Exercício 5 — Enviando Cookies ao Servidor
Execute o comando:
```bash
curl -i -b cookies.txt https://httpbin.org/cookies
```
**Perguntas:**
- O cookie foi enviado corretamente?
- Qual informação aparece na resposta?

---

### Exercício 6 — Requisição HTTP Manual (Porta 80)
Execute o comando:
```bash
nc example.com 80
```
Depois digite a requisição:
```http
GET / HTTP/1.1
Host: example.com
Connection: close

```
**Perguntas:**
- O que o servidor retorna?
- Você consegue identificar o código de status HTTP?

---

### Exercício 7 — Requisição HTTPS Manual (Porta 443)
Execute o comando:
```bash
echo -e "GET / HTTP/1.1\r\nHost: www.uol.com.br\r\nConnection: close\r\n\r\n" | openssl s_client -connect www.uol.com.br:443 -quiet
```
**Perguntas:**
- O conteúdo retornado é legível?
- Por que precisamos do `openssl s_client` em vez do `nc`?
- Qual a principal diferença entre HTTP e HTTPS?

---

### Exercício 8 — Interpretação de Códigos HTTP
Com base nos exercícios anteriores:
**Perguntas:**
- Qual o significado de:
  - `200 OK`
  - `404 Not Found`
- Em que situações cada um ocorre?
- O `curl` mostra o corpo da resposta nesses casos?

---

### Exercício 9 — Verificação de Modificação de Página (Wikipedia)
Você deseja verificar se a página inicial da Wikipedia foi modificada recentemente. Execute:
```bash
curl -I https://www.wikipedia.org
```
**Perguntas:**
- A página foi trazida do servidor hoje?
- Qual é o valor do campo `Last-Modified`?
- A página parece recente?

---

### Exercício 10 — Requisição Condicional com `If-Modified-Since`
Execute o comando:
```bash
curl -I -H "If-Modified-Since: Sat, 14 Mar 2026 15:00:00 GMT" https://www.wikipedia.org
```
**Perguntas:**
- O servidor retornou `HTTP/2 304 Not Modified` ou `200 OK`?
- O que isso indica sobre a página?

---

### Exercício 11 — Interpretação do GET Condicional
**Perguntas:**
- O que significa `HTTP/2 304 Not Modified`?
- Em que situação o cliente evita baixar o conteúdo?
- Qual a vantagem disso em termos de desempenho e uso de rede?

---

### Exercício 12 — Peer-to-Peer (P2P)
**Perguntas:**
- Por que o tempo para a distribuição de conteúdo não cresce linearmente em redes P2P? 
- Considerando que $N$ é o número de hospedeiros que recebem o conteúdo, por que o tempo no modelo cliente-servidor cresce de forma distinta do modelo P2P?
