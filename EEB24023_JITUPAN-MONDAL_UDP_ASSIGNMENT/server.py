import socket

SERVER_IP = '10.0.0.1'
PORT = 5001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, PORT))

received_seqs = set()
duplicates = 0

print("Server is listening...")

while len(received_seqs) < 10:
    data, addr = sock.recvfrom(1024)
    message = data.decode()
    
    parts = message.split('|')
    seq = int(parts[0])
    msg = parts[1]
    
    ack = f"ACK|{seq}"
    sock.sendto(ack.encode(), addr)
    
    if seq in received_seqs:
        duplicates += 1
        print(f"Duplicate detected: {message}")
    else:
        received_seqs.add(seq)
        print(f"Received: {message}")

print(f"TOTAL_UNIQUE_MESSAGES_RECEIVED={len(received_seqs)}")
print(f"TOTAL_DUPLICATES_DETECTED={duplicates}")
print("STATUS=SUCCESS")

sock.close()