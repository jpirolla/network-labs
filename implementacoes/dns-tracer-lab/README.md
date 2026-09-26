# dns-tracer — Ferramenta de Análise DNS em Wire Format

Ferramenta Python que constrói e envia **pacotes DNS em wire format** (RFC 1035) sem dependências externas, demonstrando o protocolo DNS no nível de bits e bytes.

## Objetivo

Compreender o protocolo DNS além da camada de aplicação — construindo manualmente os campos do cabeçalho e da seção de questão em formato binário, exatamente como o protocolo especifica.

## Conceitos praticados

### Protocolo DNS (RFC 1035)
- Estrutura de um pacote DNS: **Header** (12 bytes) + **Question section**
- Campos do Header: `ID`, `FLAGS`, `QDCOUNT`, `ANCOUNT`, `NSCOUNT`, `ARCOUNT`
- Flags de 16 bits: `QR | OPCODE | AA | TC | RD | RA | Z | RCODE`
- Codificação de **QNAME** como labels com comprimento prefixado:
  - `"google.com"` → `\x06google\x03com\x00`
- Tipos de registro suportados: **A**, **AAAA**, **NS**, **CNAME**, **SOA**, **MX**, **ANY**
- **QCLASS IN** (Internet) = 1
- Transporte sobre **UDP** (sem dependências externas)

### Programação
- `struct.pack("!HHHHHH", ...)` — serialização de inteiros em big-endian (network byte order)
- Sockets UDP de baixo nível
- Geração de `transaction_id` aleatório com `os.urandom(2)`

## Implementação

```
dns-tracer-lab/
├── dns_tracer/
│   ├── __init__.py     → versão do pacote
│   └── packet.py       → construção do pacote DNS em wire format
└── pyproject.toml      → configuração do projeto (entry point: dns-tracer)
```

### Módulo `packet.py`

| Função | Descrição |
|--------|-----------|
| `build_query(domain, qtype, ...)` | Constrói pacote DNS completo (header + question) |
| `encode_qname(domain)` | Codifica domínio no formato DNS wire (labels com comprimento) |
| `_build_flags(recursion_desired)` | Monta os 16 bits de flags do header |

## Como instalar e usar

```bash
cd implementacoes/dns-tracer-lab

# Instalar como pacote
pip install -e .

# Usar via CLI (quando entry point estiver implementado)
dns-tracer google.com A
dns-tracer github.com AAAA
```

## Relação com os laboratórios

Este projeto complementa diretamente o [a06 — Análise DNS com Wireshark](../../laboratorios/a06-wireshark-dns/): enquanto o Wireshark captura e analisa pacotes DNS gerados por outros aplicativos, esta ferramenta *constrói* os mesmos pacotes do zero, expondo cada campo do protocolo.

## Referências

- [RFC 1035 — Domain Names: Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035)
- Kurose, J. F.; Ross, K. W. — *Computer Networking: A Top-Down Approach*, Seção 2.4 (DNS)
