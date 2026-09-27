# Roteiro de Configuração — OSPFv3 em Redes IPv6 Multiárea

## Requisitos Gerais

1. Desenvolver a rede IPv6 conforme a topologia e o roteiro abaixo.
2. **Desafio:** Criar uma expansão com uma 4ª área OSPFv3 conectada ao backbone.

---

## Topologia e Endereçamento

### Estrutura de Áreas IPv6:
- **Área 0 (Backbone):** `2001:0::/32`
  - Rede 1: `2001:0:1::/64`
  - Rede 2: `2001:0:2::/64`
- **Área 1:** `2001:1::/32`
  - Rede 1: `2001:1:1::/64`
- **Área 2:** `2001:2::/32`
  - Rede 1: `2001:2:1::/64`

### Dispositivos:
- 3 Roteadores Cisco ISR 4331 (suportam IPv6)

### Conexões Físicas:
- Roteador 0 (`Gig 0/0/0`) $\rightarrow$ Roteador 1 (`Gig 0/0/0`)
- Roteador 0 (`Gig 0/0/1`) $\rightarrow$ Roteador 2 (`Gig 0/0/0`)
- Roteador 1 (`Gig 0/0/1`) $\rightarrow$ Switch 1
- Roteador 2 (`Gig 0/0/1`) $\rightarrow$ Switch 2

---

## Roteiro de Configuração CLI (Cisco IOS)

### Roteador 0
```cisco
enable
configure terminal
ipv6 unicast-routing
ipv6 router ospf 1
 router-id 10.0.0.0
 exit

# Conexão com Roteador 1 (Área 0)
interface gig 0/0/0
 ipv6 enable
 ipv6 ospf 1 area 0
 ipv6 address 2001:0:1::1/64
 no shutdown
 exit

# Conexão com Roteador 2 (Área 0)
interface gig 0/0/1
 ipv6 enable
 ipv6 ospf 1 area 0
 ipv6 address 2001:0:2::1/64
 no shutdown
 exit
```

### Roteador 1
```cisco
enable
configure terminal
ipv6 unicast-routing
ipv6 router ospf 1
 router-id 10.0.0.1
 exit

# Conexão com Roteador 0 (Área 0)
interface gig 0/0/0
 ipv6 enable
 ipv6 ospf 1 area 0
 ipv6 address 2001:0:1::2/64
 no shutdown
 exit

# Conexão com a LAN (Área 1)
interface gig 0/0/1
 ipv6 enable
 ipv6 ospf 1 area 1
 ipv6 address 2001:1:1::1/64
 no shutdown
 exit
```

### Roteador 2
```cisco
enable
configure terminal
ipv6 unicast-routing
ipv6 router ospf 1
 router-id 10.0.0.2
 exit

# Conexão com Roteador 0 (Área 0)
interface gig 0/0/0
 ipv6 enable
 ipv6 ospf 1 area 0
 ipv6 address 2001:0:2::2/64
 no shutdown
 exit

# Conexão com a LAN (Área 2)
interface gig 0/0/1
 ipv6 enable
 ipv6 ospf 1 area 2
 ipv6 address 2001:2:1::1/64
 no shutdown
 exit
```

---

## Configuração dos Dispositivos Finais (Hosts)

1. Habilitar a autoconfiguração de gateway IPv6 dinâmico nos hosts.
2. Acelerar o tempo no Packet Tracer (`Alt + D`).
3. Realizar testes de comunicação via `ping` entre dispositivos de áreas distintas.
