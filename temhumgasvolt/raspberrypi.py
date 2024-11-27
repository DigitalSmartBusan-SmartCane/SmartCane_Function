# 라즈베리파이 코드
# 아두이노-라즈베리파이-윈도우로 데이터를 전송하기 위한 코드
# send.py


import serial
import socket
import time

# 시리얼 포트 설정
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

# 서버 소켓 설정
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 9999))  # 모든 IP에서 접속 허용, 포트 9999
server_socket.listen(1)
print("Waiting for connection...")

# 클라이언트(윈도우)가 연결될 때까지 대기
client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address} established.")

# 데이터 읽어서 클라이언트로 전송
try:
    while True:
        data = arduino.readline().decode('utf-8').strip()  # \r, \n 제거
        if data:
            if "ppm" in data:  # ppm, temp, humi, volt, time 데이터일 때
                parts = data.split(", ")
                try:
                    ppm = float(parts[0].split(":")[1].strip())
                    temp = float(parts[1].split(":")[1].strip())
                    humi = float(parts[2].split(":")[1].strip())
                    volt = float(parts[3].split(":")[1].strip())
                    time_sec = int(parts[4].split(":")[1].strip())

                    message = f"{ppm},{temp},{humi},{volt},{time_sec}"
                    print(f"Sending data: {message}")  # 전송하는 데이터 확인
                    client_socket.sendall(message.encode('utf-8'))  # 클라이언트로 데이터 전송
                except IndexError as e:
                    print(f"Error processing data: {e}")
                    continue
                except ValueError as e:
                    print(f"ValueError: {e}")
                    continue

        time.sleep(0.8)  # 1초마다 읽기 (데이터 갱신 여부 확인 후 전송)
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    client_socket.close()
    server_socket.close()