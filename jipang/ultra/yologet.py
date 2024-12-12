import RPi.GPIO as GPIO
import time
import socket
import threading

# 초음파 센서 핀 설정
TRIG = 23
ECHO = 24

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# 스레드 동기화 이벤트
server_ready_event = threading.Event()

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
    distance = pulse_duration * 17150
    return round(distance, 2) if 0 < distance < 400 else None

# 윈도우로 초음파 데이터 전송 (클라이언트 역할)
def send_ultrasound_data():
    windows_ip = '192.168.0.133'  # 윈도우 IP
    windows_port = 5000
    ultrasound_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ultrasound_socket.connect((windows_ip, windows_port))
    print("윈도우에 초음파 데이터 전송 준비 완료 (포트 5000)")

    try:
        while True:
            distance = measure_distance()
            if distance is not None:
                print(f"Measured Distance = {distance} cm")
                ultrasound_socket.sendall(f"Distance: {distance} cm".encode('utf-8'))
            time.sleep(1)
    except Exception as e:
        print(f"초음파 데이터 전송 실패: {e}")
    finally:
        ultrasound_socket.close()

# 윈도우에서 객체 탐지 결과 수신 (서버 역할)
def receive_object_detection_results():
    raspberry_port = 5001
    result_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    result_socket.bind(('0.0.0.0', raspberry_port))
    result_socket.listen(1)
    print("객체 탐지 결과 대기 중 (포트 5001)...")
    server_ready_event.set()  # 서버 준비 완료 신호 전송
    result_conn, addr = result_socket.accept()
    print(f"윈도우와 연결됨: {addr}")

    try:
        while True:
            data = result_conn.recv(1024)
            if data:
                print(f"객체 탐지 결과 수신: {data.decode('utf-8')}")
    except Exception as e:
        print(f"객체 탐지 결과 수신 실패: {e}")
    finally:
        result_conn.close()
        result_socket.close()

# 멀티스레드로 서버와 클라이언트 동시에 실행
ultrasound_thread = threading.Thread(target=send_ultrasound_data)
object_detection_thread = threading.Thread(target=receive_object_detection_results)

ultrasound_thread.start()
object_detection_thread.start()

ultrasound_thread.join()
object_detection_thread.join()
