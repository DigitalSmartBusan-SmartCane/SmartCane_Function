import RPi.GPIO as GPIO
import time
import socket
import threading

# 초음파 센서 핀 설정
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# 초음파 거리 측정 함수
def measure_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # 단위: cm
    return round(distance, 2) if 0 < distance < 400 else None

# YOLO 탐지 결과 수신 (서버 역할)
def receive_detection_results():
    detection_port = 5001
    detection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    detection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    detection_socket.bind(('0.0.0.0', detection_port))
    detection_socket.listen(1)
    print("YOLO 탐지 결과 수신 대기 중 (포트 5001)...")

    while True:
        detection_conn, addr = detection_socket.accept()
        print(f"클라이언트 연결됨: {addr}")

        try:
            while True:
                data = detection_conn.recv(1024)
                if not data:
                    print("클라이언트 연결 끊김.")
                    break
                print(f"YOLO 탐지 결과 수신: {data.decode('utf-8')}")
        except Exception as e:
            print(f"데이터 수신 오류: {e}")
        finally:
            detection_conn.close()

if __name__ == "__main__":
    threading.Thread(target=receive_detection_results).start()
