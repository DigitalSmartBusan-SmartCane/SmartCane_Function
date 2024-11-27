// 아두이노 코드
// 실시간 온도,습도,전압,가스농도를 측정함
// 심장박동이랑 같이하면 복잡해서 심장박동은 따로 뺐음



#include <MQUnifiedsensor.h>         // MQ-5 가스 센서 라이브러리 포함
#include <DHT.h>                     // DHT11 온습도 센서 라이브러리 포함

// MQ-5 정의
#define placa "Arduino UNO"
#define Voltage_Resolution 5
#define MQ5_pin A0                  // MQ-5 센서의 아날로그 입력 핀
#define MQ5_type "MQ-5"
#define ADC_Bit_Resolution 10
#define RatioMQ6CleanAir 10

MQUnifiedsensor MQ5(placa, Voltage_Resolution, ADC_Bit_Resolution, MQ5_pin, MQ5_type);

// DHT11 정의
#define DHTPIN 4                    // DHT11 데이터 핀
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// 전압 측정에 사용될 저항 값
#define R1 220.0
#define R2 4700.0

unsigned long previousMillis = 0;  // 이전 시간 추적 변수
unsigned long bpmMillis = 0;       // BPM 측정을 위한 시간 변수
int seconds = 0;                   // 초 단위 시간 변수

// 진동 모듈 핀
const int VIBRATION_PIN = 3;   // 진동 모듈 핀

void setup() {
  Serial.begin(9600);  // 시리얼 모니터 시작

  // 진동 모듈 핀 초기화
  pinMode(VIBRATION_PIN, OUTPUT);
  digitalWrite(VIBRATION_PIN, LOW); // 초기 상태는 OFF

  // DHT11 초기 설정
  dht.begin();
  
  // MQ-5 초기 설정
  MQ5.setRegressionMethod(1); // _PPM = a * ratio^b
  MQ5.setA(2127.2); 
  MQ5.setB(-2.526);
  MQ5.init();

  // MQ-5 보정
 
  float calcR0 = 0;
  for (int i = 1; i <= 10; i++) {
    MQ5.update();
    calcR0 += MQ5.calibrate(RatioMQ6CleanAir);
    
  }
  MQ5.setR0(calcR0 / 10);
  

  if (isinf(calcR0)) {
    Serial.println("Warning: Connection issue, R0 is infinite (open circuit detected), please check wiring.");
    while (1);
  }
  if (calcR0 == 0) {
    Serial.println("Warning: Connection issue, R0 is zero (short circuit detected), please check wiring.");
    while (1);
  }

}

void loop() {
  unsigned long currentMillis = millis();  // 현재 시간

  // 1초마다 데이터를 측정하고 출력
  if (currentMillis - previousMillis >= 1000) {
    previousMillis = currentMillis;  // 이전 시간 업데이트
    seconds++;  // 초 단위로 증가

    // MQ-5 센서 데이터 읽기
    MQ5.update();
    float ppm = MQ5.readSensor();
    Serial.print("ppm: ");
    Serial.print(ppm);
    Serial.print(", ");
    
    // DHT11 온습도 데이터 읽기
    float temp = dht.readTemperature();
    float humi = dht.readHumidity();
    
    if (isnan(humi) || isnan(temp)) {
      Serial.println("Failed to read from DHT sensor!");
    } else {
      Serial.print("temp: ");
      Serial.print(temp);
      Serial.print(", humi: ");
      Serial.print(humi);
      Serial.print(", ");
    }
    
    // 전압 측정
    int data = analogRead(A1); // A1 핀에서 아날로그 값 읽기
    float volt = (5 * data / 1024.0) / (R2 / (R1 + R2));
    Serial.print("volt: ");
    Serial.print(volt);
    Serial.print(", ");

    // 진동 모듈 켜기/끄기
    if (temp > 60 || ppm > 1000 || humi > 85 || volt > 4.3 || volt < 2.5) {
      digitalWrite(VIBRATION_PIN, HIGH); // 진동 모듈 켜기
    } else {
      digitalWrite(VIBRATION_PIN, LOW); // 진동 모듈 끄기
    }

    // 초 단위 시간 출력
    Serial.print("time: ");
    Serial.println(seconds);
  }
}