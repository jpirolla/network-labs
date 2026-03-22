import socket
import select
import time
import sys
from prometheus_client import start_http_server, Counter, Gauge, Histogram

# PROMETHEUS METRICS
# Gauge: active connections per client (IP + port)
ACTIVE_CONNECTIONS = Gauge(
    'active_connections', 
    'Active connections per client', 
    ['client_ip', 'client_port']
)

# Counter: total messages and bytes received
MESSAGES_RECEIVED = Counter(
    'messages_received_total', 
    'Total messages received', 
    ['client_ip', 'client_port']
)
BYTES_RECEIVED = Counter(
    'bytes_received_total', 
    'Total bytes received', 
    ['client_ip', 'client_port']
)

# Histogram: measure latency from client send -> server receive
PROCESSING_LATENCY = Histogram(
    'message_latency_seconds',
    'Message latency (Client -> Server)',
    ['client_ip', 'client_port']
)


# State dictionaries
clients = {}  # Map socket -> (IP, port)
stats = {}    # Map (IP, port) -> number of messages received

def mostrar_dashboard():
    """
    Clears terminal and displays a real-time dashboard.
    Shows demultiplexed TCP flows (per client IP + port) and active connections.
    """
    sys.stdout.write('\033[2J\033[H')
    
    print("="*60)
    print(f"{'MULTIPLEXING DASHBOARD (TCP/Transport Layer)':^60}")
    print("="*60)
    print(f"{'Source IP':<18} | {'Source Port':<15} | {'Messages Received'}")
    print("-" * 60)
    
    if not stats:
        print(f"{'No clients connected.':^60}")
    else:
        for (ip, porta), reqs in stats.items():
            print(f"{ip:<18} | {porta:<15} | {reqs}")
    
    print("="*60)
    print(f"Total active connections: {len(clients)}")
    print("Server waiting for data (using select)...")
    sys.stdout.flush()

def main():
    # CREATE TCP SERVER SOCKET

    # socket.AF_INET -> IPv4 address type
    # socket.SOCK_STREAM -> TCP (connection-oriented)
    # setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) -> Allows reuse of the port quickly if 
    # the server is restarted, avoiding "address already in use"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind(("0.0.0.0", 5000)) ->  socket on the server's IP and port 5000
    # 0.0.0.0 -> Accepts connections from any network interface
    # listen(10) -> Enables the socket to accept connections, with a queue of 10 pending connections
    
    server.bind(("0.0.0.0", 5000))
    server.listen(10) 
    
    sockets_monitorados = [server]  # list of sockets to monitor (server + clients)
    ultimo_update = time.time()
    
    # start Prometheus HTTP server for metrics scraping
    start_http_server(8000)
    mostrar_dashboard()
    
    while True:
        agora = time.time()
        
        # I/O Multiplexing
        # Use select to wait for any socket to be ready for reading
        ready_to_read, _, _ = select.select(sockets_monitorados, [], [], 1.0)
        
        for sock in ready_to_read:
            if sock == server:
                # NEW CLIENT CONNECTION
                # server.accept() is blocking: waits until a client connects
                # Returns a tuple (client_socket, client_address)
                # - client_socket: new socket for communication with this client
                # - client_address: tuple (IP, port)
                # The original server socket continues to listen for new connections

                client_socket, client_address = server.accept()
                
                # add client socket to monitoring list for select()
                sockets_monitorados.append(client_socket)
                
                # track client socket -> (IP, port) for demux
                clients[client_socket] = client_address
                stats[client_address] = 0
                
                # update Prometheus gauge
                ip, porta = client_address
                ACTIVE_CONNECTIONS.labels(client_ip=ip, client_port=str(porta)).set(1)
                
            else:
                # existing client sent data
                try:
                    # Receive up to 1024 bytes from client
                    # recv() blocks if there's no data (unless socket is non-blocking)
                    # If recv() returns b'' → client disconnected
                    data = sock.recv(1024)
                    if data:
                        addr = clients[sock]
                        ip, porta = addr
                        stats[addr] += 1
                        
                        # calculate latency if payload has timestamp
                        try:
                            texto = data.decode()
                            partes = texto.split('|')
                            if len(partes) >= 3:
                                ts_envio = float(partes[2])
                                latencia = agora - ts_envio
                                PROCESSING_LATENCY.labels(client_ip=ip, client_port=str(porta)).observe(latencia)
                        except Exception:
                            pass

                        # update Prometheus counters
                        MESSAGES_RECEIVED.labels(client_ip=ip, client_port=str(porta)).inc()
                        BYTES_RECEIVED.labels(client_ip=ip, client_port=str(porta)).inc(len(data))
                        
                        # send ACK back to client (simulating reliable TCP response)
                        resposta = f"ACK: Msg #{stats[addr]} received"
                        sock.send(resposta.encode())
                    else:
                        # client closed connection (EOF)
                        addr = clients[sock]
                        ip, porta = addr
                        sockets_monitorados.remove(sock)
                        sock.close()
                        clients.pop(sock, None)
                        stats.pop(addr, None)
                        ACTIVE_CONNECTIONS.labels(client_ip=ip, client_port=str(porta)).set(0)
                            
                except Exception as e:
                    if sock in sockets_monitorados:
                        sockets_monitorados.remove(sock)
                    addr = clients.get(sock, ("Unknown", 0))
                    if sock in clients:
                        sock.close()
                        clients.pop(sock, None)
                    stats.pop(addr, None)
                    if addr[0] != "Unknown":
                        ip, porta = addr
                        ACTIVE_CONNECTIONS.labels(client_ip=ip, client_port=str(porta)).set(0)

        # refresh dashboard 
        if agora - ultimo_update >= 0.5:
            mostrar_dashboard()
            ultimo_update = agora

if __name__ == "__main__":
    main()