# Implementação de Máscaras de Redes — VLSM com DHCP e DNS

## Enunciado

Implemente uma rede baseada no bloco `192.168.1.0/24`, utilizando **VLSM** (*Variable Length Subnet Mask*), subdividindo a rede em sub-redes de tamanhos diferentes sem sobreposição de endereços.

### Sub-redes Iniciais:
- **LAN 1:** `192.168.1.0/26`
- **LAN 2:** `192.168.1.64/26`
- **Link entre Roteadores:** `192.168.1.252/30`

---

## Requisitos

### Roteadores
- Configurar IPs nas interfaces.
- Habilitar **RIP v2**:
```cisco
router rip
 version 2
 no auto-summary
 network 192.168.1.0
```

### Servidor (LAN 1)
- **IP Fixo:** `192.168.1.2`
- Configurar os serviços de **DHCP** e **DNS**.

### DHCP
- Distribuir IP para todas as LANs.
- Configurar Gateway Padrão e servidor DNS nos pools.
- Usar `ip helper-address` no roteador remoto para atender redes distribuídas.

### DNS
- Criar um registro de nome (ex: `www.tabeladeprodutos.com.br`) apontando para o servidor da LAN 2.

---

## Desafio

Adicionar uma terceira rede local à topologia:
- **LAN 3:** `192.168.1.224/27`

> **Restrição:** Não pode haver sobreposição de endereços com as demais sub-redes. Ajustar o roteamento RIP v2 e os pools DHCP para incluir esta nova rede.

---

## Testes de Validação
1. Comunicação (ping) entre todas as sub-redes.
2. Clientes obtendo endereço IP automaticamente via DHCP em todas as LANs.
3. Resolução de nomes via DNS a partir de qualquer host.
