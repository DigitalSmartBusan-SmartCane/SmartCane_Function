import socket
import time
from collections import Counter
from ultralytics import YOLO
import cv2

# YOLOv5 모델 로드   /api 자체는 yolov8을 쓰고 있는데 상관없음 (ulyralystic이 yolov의 기본라이브러리) / 가중치 모델은 yolov5기반 학습 
model = YOLO('best.pt')

# 라즈베리파이 카메라 스트리밍 URL 설정
stream_url = 'http://172.20.10.3:8000/stream.mjpg'

# 라즈베리파이 IP 및 포트 설정
raspberry_ip = '172.20.10.3'  # 라즈베리파이 IP
raspberry_port = 5000

# 비디오 스트림 열기
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("오류: 비디오 스트림을 열 수 없습니다.")
    exit()

# 라즈베리파이와 소켓 연결 설정
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((raspberry_ip, raspberry_port))
    print("라즈베리파이와 연결 성공")
except Exception as e:
    print(f"소켓 연결 실패: {e}")
    exit()

last_sent_data = ""  # 이전에 전송한 데이터 저장

while True:
    start_time = time.time()

    ret, frame = cap.read()

    if not ret:
        print("프레임을 가져오지 못했습니다.")
        break

    # YOLOv8 객체 인식 실행
    results = model(frame)

    detected_objects = []

    # 인식된 객체들 반복 처리
    for result in results:
        for box in result.boxes:
            # 신뢰도와 클래스 ID 가져오기
            conf = box.conf[0]
            class_id = box.cls[0].item()
            class_name = model.names[class_id]

            # 신뢰도 0.5 이상인 경우에만 처리
            if conf >= 0.5:
                detected_objects.append(class_name)

    # 객체 탐지 결과 요약
    if detected_objects:
        object_counts = Counter(detected_objects)
        summary = ', '.join([f"{key} {value}" for key, value in object_counts.items()])

        # 이전 데이터와 비교 후 전송
        if summary != last_sent_data:
            try:
                sock.sendall(summary.encode('utf-8'))
                print(f"객체 탐지 결과 전송: {summary}")
                last_sent_data = summary
            except Exception as e:
                print(f"객체 탐지 결과 전송 실패: {e}")

 

# 리소스 해제
cap.release()
sock.close()
