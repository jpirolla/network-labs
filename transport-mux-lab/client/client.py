import socket
import time
import os
import random
import threading

def cliente_worker(worker_id):
    """
    Worker function for a single connection lifecycle.
    Each thread simulates an independent TCP flow (Multiplexed at transport layer).
    """
    while True:
        # random delay before connecting to simulate realistic traffic
        time.sleep(random.uniform(0.5, 3.0))

        # create a TCP socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to the server
        try:
            client.connect(("server", 5000))
            hostname = os.getenv('HOSTNAME', 'unknown_container')
            thread_name = f"Thread-{worker_id}"
            
            # random number of messages per session (simulate burst traffic)
            mensagens_na_sessao = random.randint(3, 10)
            
            for i in range(mensagens_na_sessao):
                # payload includes hostname, thread identifier, counter, timestamp
                # timestamp is used later to calculate latency on server
                msg = f"{hostname}:{thread_name}|{i+1}|{time.time()}"
                client.send(msg.encode())  # Send message via TCP

                # Wait for ACK from server (demonstrates reliable TCP delivery)
                response = client.recv(1024)
                if not response:
                    break  # onnection closed by server
                    
                # short random delay to simulate traffic bursts
                time.sleep(random.uniform(0.1, 0.5))
                
            print(f"[{hostname} | {thread_name}] Finished session. Disconnecting...")
            
        except ConnectionRefusedError:
            print("Server is offline...")
            time.sleep(2)
        except Exception as e:
            pass
        finally:
            client.close()  # close TCP connection properly

def main():
    NUM_THREADS = 5  # number of parallel TCP flows (threads)
    threads = []
    
    print(f"Starting multiplexed client with {NUM_THREADS} parallel threads...")
    
    # start multiple threads to simulate transport-layer multiplexing
    for i in range(NUM_THREADS):
        t = threading.Thread(target=cliente_worker, args=(i+1,))
        t.daemon = True  # daemon threads exit when main program exits
        t.start()
        threads.append(t)
        
    # keep main thread alive while workers send messages
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()