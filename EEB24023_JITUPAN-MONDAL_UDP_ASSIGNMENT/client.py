import socket
import time

SERVER_IP   = '10.0.0.1'
PORT        = 5001
TIMEOUT     = 0.7
TOTAL_MSGS  = 10
LOSS_PERCENT = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(TIMEOUT)   

total_packets_sent    = 0
total_retransmissions = 0

start_time = time.time()

for seq in range(1, TOTAL_MSGS + 1):

    packet    = f"{seq}|Message {seq} from h2"   
    ack_received = False

    while not ack_received:

        sock.sendto(packet.encode(), (SERVER_IP, PORT))
        total_packets_sent += 1
        print(f"Sent: {packet}")

        try:
            data, _ = sock.recvfrom(1024)
            ack     = data.decode()            

            if ack == f"ACK|{seq}":
                print(f"ACK received for message {seq}")
                ack_received = True             

        except socket.timeout:
            print(f"Timeout! Retransmitting message {seq}...")
            total_retransmissions += 1

transfer_time = round(time.time() - start_time, 3)

print(f"\nTOTAL_MESSAGES={TOTAL_MSGS}")
print(f"LOSS_PERCENT={LOSS_PERCENT}")
print(f"TIMEOUT={TIMEOUT}")
print(f"TOTAL_PACKETS_SENT={total_packets_sent}")
print(f"TOTAL_RETRANSMISSIONS={total_retransmissions}")
print(f"TRANSFER_TIME_SECONDS={transfer_time}")
print("STATUS=SUCCESS")

sock.close()