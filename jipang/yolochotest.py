import socket
import time
import RPi.GPIO as GPIO
from gtts import gTTS
import os

# 초음파 센서 핀 설정
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# 소켓 서버 설정
host = '0.0.0.0'
port = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))
server_socket.listen(1)

print("소켓 서버 실행 중... 클라이언트를 기다리는 중입니다.")
client_socket, addr = server_socket.accept()
print(f"클라이언트 연결됨: {addr}")

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2
    return distance

# 최근 출력된 객체 기록
last_spoken_objects = ""

try:
    while True:
        # 거리 측정
        distance = measure_distance()
        print(f"측정 거리: {distance:.2f} cm")

        if distance <= 100:  # 1m 이내
            data = client_socket.recv(1024).decode('utf-8')
            print(f"수신한 객체 탐지 결과: {data}")

            if data != last_spoken_objects:  # 중복 출력 방지
                last_spoken_objects = data

                # TTS로 스피커 출력 (한국어)
                tts = gTTS(text=f"탐지된 객체는 {data}입니다.", lang='ko')
                tts.save("result.mp3")
                os.system("mpg321 result.mp3")

        time.sleep(1)

except KeyboardInterrupt:
    print("프로그램 종료")
    GPIO.cleanup()
    client_socket.close()
    server_socket.close()
