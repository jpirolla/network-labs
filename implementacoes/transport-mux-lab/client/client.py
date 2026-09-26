import socket
import time
import os
import random
import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def cliente_worker(worker_id):
    """
    Manages one full connection lifecycle: connect → send N messages → disconnect.
    Each thread creates its own socket, receiving a unique ephemeral port from the kernel,
    which makes transport-layer multiplexing observable in Grafana.
    """
    hostname = os.getenv('HOSTNAME', 'unknown_container')
    thread_name = f"Thread-{worker_id}"

    while True:
        # random delay before connecting to simulate realistic traffic patterns
        time.sleep(random.uniform(0.5, 3.0))

        # create a new TCP socket for this session
        # (each call to socket.socket() produces a unique file descriptor ->  unique ephemeral port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client.connect(("server", 5000))
            logger.info(f"[{hostname} | {thread_name}] Connected to server.")

            # random number of messages per session (simulate burst traffic)
            mensagens_na_sessao = random.randint(3, 10)

            for i in range(mensagens_na_sessao):
                # payload: hostname, thread id, message counter, send timestamp
                # the timestamp is used by the server to calculate application-level latency
                msg = f"{hostname}:{thread_name}|{i+1}|{time.time()}"
                client.send(msg.encode())

                # Wait for ACK from server (demonstrates reliable TCP delivery)
                response = client.recv(1024)
                if not response:
                    break  # connection closed by server

                # short random delay to simulate inter-message bursts
                time.sleep(random.uniform(0.1, 0.5))

            logger.info(f"[{hostname} | {thread_name}] Finished session. Disconnecting.")

        except ConnectionRefusedError:
            logger.warning(f"[{hostname} | {thread_name}] Server is offline. Retrying in 2s...")
            time.sleep(2)
        except Exception as e:
            # log unexpected errors so they are visible for debugging
            logger.error(f"[{hostname} | {thread_name}] Unexpected error: {e}", exc_info=True)
        finally:
            client.close()  # always close TCP connection properly


def main():
    NUM_THREADS = 5  # number of parallel TCP flows (threads)
    threads = []

    logger.info(f"Starting multiplexed client with {NUM_THREADS} parallel threads.")

    # start multiple threads to simulate transport-layer multiplexing
    # each thread ->  independent socket ->  unique ephemeral port ->  isolated TCP flow
    for i in range(NUM_THREADS):
        t = threading.Thread(target=cliente_worker, args=(i+1,), name=f"Worker-{i+1}")
        t.daemon = True  # daemon threads exit when main program exits
        t.start()
        threads.append(t)

    # keep main thread alive while workers send messages
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()