import socket
import select
import time
import sys
import logging
from prometheus_client import start_http_server, Counter, Gauge, Histogram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [server] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


# PROMETHEUS METRICS
# Gauge: current active connections tracked per (IP, port) tuple
# Demonstrates demultiplexation: each unique tuple -> one row in Grafana timeline
ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Active connections per client',
    ['client_ip', 'client_port']
)

# Counters: accumulate over the lifetime of the server process
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

# Histogram: latency between client send timestamp and server receive time.
# NOTE: this measures application-level latency, NOT network RTT.
# Negative values can occur due to time.time() jitter and OS scheduler
# variability between containers (even sharing the host clock). This is an
# artefact of the measurement methodology, not a logic error.
PROCESSING_LATENCY = Histogram(
    'message_latency_seconds',
    'Message latency (client send timestamp -> server receive)',
    ['client_ip', 'client_port']
)

clients: dict = {}  # socket -> (IP, port)
stats: dict = {}    # (IP, port) -> message count


def handle_disconnection(sock, monitored_sockets):
    """
    Handle a clean client disconnection (recv() returned b'').

    The kernel has already demultiplexed the TCP FIN segment to this specific
    socket.
    """
    addr = clients[sock]
    ip, port = addr
    logger.info(f"Client disconnected cleanly: {ip}:{port}")
    monitored_sockets.remove(sock)
    sock.close()
    clients.pop(sock, None)
    stats.pop(addr, None)
    ACTIVE_CONNECTIONS.labels(client_ip=ip, client_port=str(port)).set(0)


def cleanup_client(sock, monitored_sockets, error=None):
    """
    Clean up a client socket after an unexpected error (abrupt disconnection,
    RST, etc.). Logs the error and updates Prometheus metrics.
    """
    addr = clients.get(sock, ("Unknown", 0))
    ip, port = addr
    if error:
        logger.warning(f"Error on client {ip}:{port}: {error}")
    if sock in monitored_sockets:
        monitored_sockets.remove(sock)
    if sock in clients:
        sock.close()
        clients.pop(sock, None)
    stats.pop(addr, None)
    if ip != "Unknown":
        ACTIVE_CONNECTIONS.labels(client_ip=ip, client_port=str(port)).set(0)


def show_dashboard():
    """
    Clear terminal and display a real-time view of demultiplexed TCP flows.
    Each row corresponds to a unique (IP, port) tuple — the same unit used
    by the kernel to identify a TCP connection.
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
        for (ip, port), reqs in stats.items():
            print(f"{ip:<18} | {port:<15} | {reqs}")

    print("="*60)
    print(f"Total active connections: {len(clients)}")
    print("Server waiting for data (using select())...")
    sys.stdout.flush()


def main():
    # AF_INET     -> IPv4
    # SOCK_STREAM -> TCP (connection-oriented)
    # SO_REUSEADDR -> allows fast restart without "address already in use" error
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind to all interfaces (0.0.0.0) on port 5000
    # listen(10) -> accept queue of up to 10 pending connections
    server.bind(("0.0.0.0", 5000))
    server.listen(10)
    logger.info("Server listening on 0.0.0.0:5000")

    monitored_sockets = [server]  # list of sockets select() should watch
    last_update = time.time()

    # expose Prometheus metrics at http://<host>:8000/metrics
    start_http_server(8000)
    logger.info("Prometheus metrics available at :8000/metrics")
    show_dashboard()

    while True:
        now = time.time()

        # I/O Multiplexing via select()
        # select() blocks until at least one socket in `monitored_sockets`
        # has data ready to read. Timeout 1s avoids busy-waiting.
        # This allows a single thread to handle N concurrent TCP connections.
        ready_to_read, _, _ = select.select(monitored_sockets, [], [], 1.0)

        for sock in ready_to_read:
            if sock == server:
                # New client connection
                # accept() returns (client_socket, (IP, port)).
                # The kernel has already completed the TCP 3-way handshake and
                # demultiplexed this connection to a new socket descriptor.
                client_socket, client_address = server.accept()
                monitored_sockets.append(client_socket)
                clients[client_socket] = client_address
                stats[client_address] = 0

                ip, port = client_address
                logger.info(f"New connection from {ip}:{port}")
                ACTIVE_CONNECTIONS.labels(client_ip=ip, client_port=str(port)).set(1)

            else:
                # Data from existing client
                try:
                    data = sock.recv(1024)
                    if data:
                        addr = clients[sock]
                        ip, port = addr
                        stats[addr] += 1

                        # calculate application-level latency from embedded timestamp
                        try:
                            payload = data.decode()
                            parts = payload.split('|')
                            if len(parts) >= 3:
                                send_ts = float(parts[2])
                                latency = now - send_ts
                                PROCESSING_LATENCY.labels(
                                    client_ip=ip, client_port=str(port)
                                ).observe(latency)
                        except Exception:
                            pass  # malformed payload; skip latency recording

                        MESSAGES_RECEIVED.labels(client_ip=ip, client_port=str(port)).inc()
                        BYTES_RECEIVED.labels(client_ip=ip, client_port=str(port)).inc(len(data))

                        response = f"ACK: Msg #{stats[addr]} received"
                        sock.send(response.encode())

                    else:
                        # recv() == b'' -> client sent TCP FIN (clean shutdown)
                        handle_disconnection(sock, monitored_sockets)

                except Exception as e:
                    cleanup_client(sock, monitored_sockets, error=e)

        # refresh terminal dashboard at 2 Hz
        if now - last_update >= 0.5:
            show_dashboard()
            last_update = now


if __name__ == "__main__":
    main()