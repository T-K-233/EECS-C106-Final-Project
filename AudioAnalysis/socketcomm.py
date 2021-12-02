import json
import socket

def send_cmd(results):
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", 50008))
                s.listen(1)
                s.settimeout(2)  # s
                try:
                    print("waiting for connection...")
                    conn, addr = s.accept()
                    print("connected!")
                    conn.settimeout(2)
                except:
                    continue

                with conn:
                    while True:
                        #receive dum data
                        data = conn.recv(1024)
                        if not data:
                            break
                        print(data)
                        buffer = json.dumps(results)
                        conn.sendall(buffer.encode())
        except KeyboardInterrupt:
            break

    print("server ended")