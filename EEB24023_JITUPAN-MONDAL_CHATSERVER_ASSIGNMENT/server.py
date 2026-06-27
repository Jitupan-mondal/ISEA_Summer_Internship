import socket
import threading
import datetime
import os

HOST = "0.0.0.0"
PORT = 5000

clients = {}
clients_lock = threading.Lock()

CHAT_LOG   = "chat_log.txt"
SERVER_LOG = "server_log.txt"

for f in [CHAT_LOG, SERVER_LOG]:
    if not os.path.exists(f):
        open(f, "w").close()

def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

def log_server_event(event, username, ip):
    line = f"{timestamp()},{event},{username},{ip}\n"
    with open(SERVER_LOG, "a") as f:
        f.write(line)
    print(f"[LOG] {line.strip()}")

def log_chat(username, message):
    line = f"{timestamp()},{username},{message}\n"
    with open(CHAT_LOG, "a") as f:
        f.write(line)

def broadcast(message: str):
    encoded = message.encode("utf-8")
    with clients_lock:
        for sock in list(clients.keys()):
            try:
                sock.sendall(encoded)
            except Exception:
                pass

def handle_client(conn, addr):
    ip = addr[0]
    username = None
    try:
        raw = conn.recv(1024)
        if not raw:
            conn.close()
            return
        username = raw.decode("utf-8").strip()

        with clients_lock:
            clients[conn] = username

        log_server_event("CONNECTED", username, ip)
        broadcast(f"[SERVER] {username} has joined the chat!\n")

        while True:
            data = conn.recv(4096)
            if not data:
                break
            message = data.decode("utf-8").strip()
            log_chat(username, message)
            broadcast(f"[{username}] {message}\n")

    except Exception as e:
        print(f"[ERROR] {username or addr}: {e}")
    finally:
        with clients_lock:
            if conn in clients:
                del clients[conn]
        conn.close()
        if username:
            log_server_event("DISCONNECTED", username, ip)
            broadcast(f"[SERVER] {username} has left the chat.\n")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVER] Listening on {HOST}:{PORT}")
    try:
        while True:
            conn, addr = server.accept()
            print(f"[SERVER] New connection from {addr}")
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    main()

