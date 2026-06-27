import socket
import argparse
import time
import csv

parser = argparse.ArgumentParser()
parser.add_argument("--roll_no", type=str, required=True)
parser.add_argument("--name", type=str, required=True)
args = parser.parse_args()

roll_no = args.roll_no
name = args.name

SERVER_IP = "10.0.0.1"
PORT = 5000
MESSAGE_SIZES = [128, 512, 1024]
NO_OF_MSG_PER_SIZE = 10
BANDWIDTH_MBPS = 5
DELAY_MS = 50
MODES = ["persistent", "new_connection"]

message_response_log = []
result_table = []


def receive_full_response(sock):
    response = ""
    while "\n" not in response:
        chunk = sock.recv(4096).decode()
        if not chunk:
            break
        response += chunk
    return response.strip()


for mode in MODES:
    print(f"\n=== Running mode: {mode} ===")

    for message_size in MESSAGE_SIZES:
        print(f"  Message size: {message_size} bytes")
        response_times = []
        total_bytes_sent = 0
        batch_start_time = time.time()

        if mode == "persistent":
            s = socket.socket()
            s.connect((SERVER_IP, PORT))

            for message_number in range(1, NO_OF_MSG_PER_SIZE + 1):
                payload = "A" * message_size
                message = f"{mode}|{message_number}|{message_size}|{payload}\n"
                encoded = message.encode()

                start_time = time.time()
                s.sendall(encoded)
                ack = receive_full_response(s)
                end_time = time.time()

                response_time = end_time - start_time
                response_times.append(response_time)
                total_bytes_sent += len(encoded)

                message_response_log.append([
                    roll_no, name, mode,
                    message_size, message_number, response_time
                ])

                print(f"    Msg {message_number}: ACK={ack}, RT={response_time:.6f}s")

            s.close()

        elif mode == "new_connection":
            for message_number in range(1, NO_OF_MSG_PER_SIZE + 1):
                s = socket.socket()
                s.connect((SERVER_IP, PORT))

                payload = "A" * message_size
                message = f"{mode}|{message_number}|{message_size}|{payload}\n"
                encoded = message.encode()

                start_time = time.time()
                s.sendall(encoded)
                ack = receive_full_response(s)
                end_time = time.time()

                response_time = end_time - start_time
                response_times.append(response_time)
                total_bytes_sent += len(encoded)

                message_response_log.append([
                    roll_no, name, mode,
                    message_size, message_number, response_time
                ])

                print(f"    Msg {message_number}: ACK={ack}, RT={response_time:.6f}s")
                s.close()

        batch_end_time = time.time()
        total_time = batch_end_time - batch_start_time
        avg_response_time = sum(response_times) / len(response_times)
        throughput = total_bytes_sent / total_time if total_time > 0 else 0

        result_table.append([
            roll_no, name, mode,
            BANDWIDTH_MBPS, DELAY_MS,
            message_size, NO_OF_MSG_PER_SIZE,
            avg_response_time, throughput, "SUCCESS"
        ])

        print(f"  Avg RT={avg_response_time:.6f}s | Throughput={throughput:.2f} B/s")

with open("message_response_log.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "roll_no", "name", "mode",
        "message_size_bytes", "message_number", "response_time_seconds"
    ])
    writer.writerows(message_response_log)

with open("result_table.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "roll_no", "name", "mode",
        "bandwidth_mbps", "delay_ms", "message_size_bytes",
        "total_messages", "average_response_time_seconds",
        "throughput_bytes_per_second", "status"
    ])
    writer.writerows(result_table)

print("\nExperiment complete.")
print(f"message_response_log.csv: {len(message_response_log)} rows")
print(f"result_table.csv: {len(result_table)} rows")