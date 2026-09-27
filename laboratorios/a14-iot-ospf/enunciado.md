# Laboratório — Internet das Coisas (IoT) com Roteamento OSPF e DHCP Centralizado

## Requisitos e Etapas de Desenvolvimento

1. **Replicação da Topologia Inicial e Servidor DNS:**
   - Implementar o projeto conforme demonstrado no vídeo de apoio: [http://bit.ly/3GVTHMd](http://bit.ly/3GVTHMd).
   - Configurar o servidor DNS após replicar a topologia base do vídeo.

2. **Segmentação da Rede:**
   - Dividir a topologia em duas redes distintas:
     - **Rede do Servidor:** contendo os servidores centrais (DNS/DHCP).
     - **Rede IoT:** contendo os dispositivos de Internet das Coisas (smart devices, sensores, gateway).

3. **Roteamento Dinâmico via OSPF:**
   - Configurar o protocolo de roteamento dinâmico **OSPF** para interligar e permitir o tráfego entre a rede do Servidor e a rede IoT.

4. **DHCP Centralizado:**
   - Configurar **um único servidor DHCP** para distribuir os endereços IP automaticamente para ambas as redes (utilizando `ip helper-address` no roteador se necessário).

5. **Submissão:**
   - Submeter o arquivo do Cisco Packet Tracer (`.pkt`) com a versão completa e validada.
