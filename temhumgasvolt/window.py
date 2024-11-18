# 라즈베리파이에서 데이터를 받아 json파일과 sqlite데이터시트를 저장하고
# 실시간 센서값을 화면에 나타내도록함
# 센서값의 실시간 변화 그래프는 웹에서 받아서 직접 만드는 게 더 효율적이라해서 일단 삭제했음
# get.py

import sqlite3
import socket
import json
import os
import tkinter as tk
from datetime import datetime

# 데이터베이스 파일 경로 (현재 날짜를 파일 이름으로 사용)
date_str = datetime.now().strftime("%Y%m%d_%H%M%S")  # 예: 20231114_123456
db_path = rf'C:\smart_get\data\sensor_data_{date_str}.db'

# 새로운 SQLite 데이터베이스 파일 생성
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 테이블 생성 (BPM 제거)
cursor.execute('''
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ppm REAL,
    temperature REAL,
    humidity REAL,
    voltage REAL,
    time INTEGER
)
''')
conn.commit()

# tkinter 윈도우 생성
root = tk.Tk()
root.title("Sensor Data")

# 라벨 생성
ppm_label = tk.Label(root, text="PPM: 0.0", font=('Helvetica', 16))
ppm_label.pack()
temp_label = tk.Label(root, text="Temperature: 0.0", font=('Helvetica', 16))
temp_label.pack()
humi_label = tk.Label(root, text="Humidity: 0.0", font=('Helvetica', 16))
humi_label.pack()
volt_label = tk.Label(root, text="Voltage: 0.0", font=('Helvetica', 16))
volt_label.pack()
time_label = tk.Label(root, text="Time: 0", font=('Helvetica', 16))
time_label.pack()

# JSON 파일 경로 (현재 날짜를 JSON 파일 이름으로 사용)
json_file_path = rf'C:\smart_get\data\sensor_data_{date_str}.json'

# 라즈베리파이 서버에 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
raspberry_pi_ip = '192.168.0.212'  # 라즈베리파이 IP 주소
client_socket.connect((raspberry_pi_ip, 9999))

# 데이터 처리 및 저장 함수
def update_data():
    # 서버에서 받은 데이터를 데이터베이스에 저장
    data = client_socket.recv(1024).decode('utf-8').strip()
    if data:
        print(f"Received data: {data}")  # 받은 데이터를 출력하여 확인
        
        try:
            # 데이터를 쉼표로 구분해서 나누기
            values = data.split(',')
            if len(values) == 5:  # 예상한 데이터 항목 수 (5개)가 맞는지 확인
                ppm, temp, humi, volt, time_sec = map(float, values)

                # 데이터베이스에 저장
                cursor.execute('''
                    INSERT INTO sensor_data (ppm, temperature, humidity, voltage, time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (ppm, temp, humi, volt, int(time_sec)))
                conn.commit()

                # 라벨 업데이트
                ppm_label.config(text=f"PPM: {ppm:.2f}")
                temp_label.config(text=f"Temperature: {temp:.2f}")
                humi_label.config(text=f"Humidity: {humi:.2f}")
                volt_label.config(text=f"Voltage: {volt:.2f}")
                time_label.config(text=f"Time: {int(time_sec)}")

                # JSON 파일에 저장할 데이터 생성
                sensor_data = {
                    "ppm": ppm,
                    "temperature": temp,
                    "humidity": humi,
                    "voltage": volt,
                    "time": int(time_sec)
                }

                # JSON 파일에 데이터를 추가로 저장
                if os.path.exists(json_file_path):
                    with open(json_file_path, 'r') as json_file:
                        existing_data = json.load(json_file)
                else:
                    existing_data = []

                existing_data.append(sensor_data)

                with open(json_file_path, 'w') as json_file:
                    json.dump(existing_data, json_file, indent=4)

            # 데이터 길이가 5가 아니면 그냥 건너뛰기 
            else:
                return  # 잘못된 형식의 데이터는 무시

        except ValueError:
            return  # 잘못된 형식일 때 아무 동작도 하지 않음

# 데이터 처리 루프 (매 1초마다 데이터 업데이트)
def process_data():
    update_data()
    root.after(1000, process_data)  # 1초 후에 다시 실행

# tkinter 루프 시작
root.after(1000, process_data)  # 처음 시작 시 1초 후에 첫 데이터 처리
root.mainloop()

# 소켓 연결 종료
client_socket.close()
conn.close()
