# Completed Assignment 2
import socket
import datetime

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", 5000))
s.listen(5)

print("Server listening on port 5000...")

while True:
    conn, addr = s.accept()
    print(f"Client connected: {addr[0]}")
    buffer = ""

    while True:
        data = conn.recv(4096)
        if not data:
            break

        buffer += data.decode()

        while "\n" in buffer:
            full_message, buffer = buffer.split("\n", 1)
            full_message = full_message.strip()

            if not full_message:
                continue

            parts = full_message.split("|")

            if len(parts) < 4:
                print(f"Invalid message format: {full_message}")
                continue

            mode = parts[0]
            msg_id = parts[1]
            message_size = parts[2]
            message_data = "|".join(parts[3:])

            received_size = len(message_data)
            ack_sent = f"ACK|{msg_id}|{received_size}"
            conn.sendall((ack_sent + "\n").encode())

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] mode={mode} msg_id={msg_id} size={received_size} ack={ack_sent}")

            with open("server_log.txt", "a") as f:
                f.write(f"{timestamp},{addr[0]},{mode},{msg_id},{received_size},{ack_sent}\n")

    conn.close()