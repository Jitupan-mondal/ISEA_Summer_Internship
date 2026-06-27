import socket
import threading

SERVER_IP   = "10.0.0.1"
SERVER_PORT = 5000

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("\n[CLIENT] Disconnected from server.")
                break
            print(data.decode("utf-8"), end="", flush=True)
        except Exception:
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_IP, SERVER_PORT))
        print(f"[CLIENT] Connected to {SERVER_IP}:{SERVER_PORT}")
    except Exception as e:
        print(f"[CLIENT] Could not connect: {e}")
        return

    username = input("Enter Username: ").strip()
    sock.sendall(username.encode("utf-8"))

    recv_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    recv_thread.start()

    try:
        while True:
            msg = input()
            if msg.strip() == "":
                continue
            if msg.strip().lower() == "/quit":
                break
            sock.sendall(msg.encode("utf-8"))
    except (KeyboardInterrupt, EOFError):
        print("\n[CLIENT] Exiting.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()

