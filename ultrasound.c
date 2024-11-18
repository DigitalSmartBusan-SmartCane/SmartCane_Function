#include <NewPing.h>

#define TRIG1 2  // 우측 초음파 센서 트리거 핀
#define ECHO1 3  // 우측 초음파 센서 에코 핀
#define TRIG2 5  // 좌측 초음파 센서 트리거 핀
#define ECHO2 4  // 좌측 초음파 센서 에코 핀
#define TRIG3 6  // 앞쪽 초음파 센서 트리거 핀
#define ECHO3 7  // 앞쪽 초음파 센서 에코 핀
#define BUZZER_PIN 11  // 부저가 연결된 핀 (PWM 지원 핀으로 설정)

#define MAX_DISTANCE 1000  // 초음파 센서 최대 거리 (단위: cm)
#define NUM_SONAR 3        // 초음파 센서 개수
#define ALERT_DISTANCE 10  // 부저가 울리기 시작하는 거리 (단위: cm)

NewPing sonar[NUM_SONAR] = {
  NewPing(TRIG1, ECHO1, MAX_DISTANCE),  // 우측
  NewPing(TRIG2, ECHO2, MAX_DISTANCE),  // 좌측
  NewPing(TRIG3, ECHO3, MAX_DISTANCE)   // 앞쪽
};

int distance[NUM_SONAR];  // 각 센서의 거리를 저장할 배열

void setup() {
  Serial.begin(9600);  // 시리얼 통신 시작
  pinMode(BUZZER_PIN, OUTPUT);  // 부저 핀을 출력 모드로 설정
}

void loop() {
  delay(50);  // 잠시 대기
  updateSonar();  // 초음파 센서 값을 업데이트
  checkDistanceAndAlert();  // 거리 확인 후 부저 울림 여부 결정

  // 시리얼 모니터에 거리 출력
  Serial.print("Distance (우측): ");
  Serial.print(distance[0]);
  Serial.print(" cm  Distance (좌측): ");
  Serial.print(distance[1]);
  Serial.print(" cm  Distance (앞쪽): ");
  Serial.println(distance[2]);
}

// 각 초음파 센서로부터 거리 값을 업데이트하는 함수
void updateSonar() {
  for (int i = 0; i < NUM_SONAR; i++) {
    distance[i] = sonar[i].ping_cm();  // 각 센서의 거리 측정
    // 측정된 거리가 0이면 MAX_DISTANCE로 설정
    if (distance[i] == 0)
      distance[i] = MAX_DISTANCE;
  }
}

// 거리 값에 따라 부저를 울리거나 끄는 함수
void checkDistanceAndAlert() {
  // 세 초음파 센서 중 하나라도 ALERT_DISTANCE 미만이면 부저 울림
  if (distance[0] < ALERT_DISTANCE || distance[1] < ALERT_DISTANCE || distance[2] < ALERT_DISTANCE) {
    analogWrite(BUZZER_PIN, 128);  // 부저를 울림 (PWM 신호로 제어)
  } else {
    analogWrite(BUZZER_PIN, 0);  // 부저 끄기
  }
}
