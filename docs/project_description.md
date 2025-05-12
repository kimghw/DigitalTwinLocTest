# 프로젝트 설명

이 문서는 프로젝트의 기술적 세부사항을 설명합니다. 디자인 패턴, 객체, 데이터 타입, 이벤트, 호출 방법 등을 상세히 기록하여 재사용할 수 있게 합니다.

## 아키텍처

### 디자인 패턴

- RESTful API: 클라이언트-서버 통신을 위한 REST 아키텍처 스타일 적용
- 지연 시뮬레이터: 다양한 지연 시나리오를 시뮬레이션하기 위한 전략 패턴 적용

### 시스템 구조

```
+----------------+        +------------------+        +----------------+
|                |        |                  |        |                |
|  유니티 앱      +------->+  REST API 서버   +------->+  지연 시뮬레이터 |
|  (클라이언트)   |        |                  |        |                |
|                |<-------+                  |<-------+                |
+----------------+        +------------------+        +----------------+
```

## 주요 컴포넌트

### REST API 서버

- 역할: 클라이언트로부터 이미지를 수신하고, 처리된 데이터를 반환
- 주요 클래스/객체: 
  - ImageController: 이미지 수신 및 처리 요청 처리
  - DelaySimulator: 다양한 지연 시나리오 시뮬레이션
- 데이터 흐름: 
  1. 클라이언트가 이미지를 서버로 전송
  2. 서버는 이미지를 처리하고 결과 데이터 생성
  3. 설정된 지연 시나리오에 따라 응답 지연
  4. 처리된 데이터를 클라이언트에게 반환

### 지연 시뮬레이터

- 역할: 다양한 지연 시나리오를 시뮬레이션
- 주요 클래스/객체:
  - DelayStrategy: 지연 전략 인터페이스
  - FixedDelayStrategy: 고정 지연 구현
  - ProgressiveIncreaseDelayStrategy: 점진적 증가 지연 구현
  - ProgressiveDecreaseDelayStrategy: 점진적 감소 지연 구현
  - StepDelayStrategy: 계단식 지연 구현
  - NoResponseDelayStrategy: 무응답 시뮬레이션 구현
  - RandomDelayStrategy: 랜덤 지연 구현
- 데이터 흐름:
  1. 서버가 지연 시뮬레이터에 지연 요청
  2. 시뮬레이터는 현재 설정된 전략에 따라 지연 시간 계산
  3. 계산된 시간만큼 응답 지연

## 데이터 모델

### 주요 데이터 타입

- Data::Image: 클라이언트에서 서버로 전송되는 이미지 데이터
- Data::PosePacket: 서버에서 클라이언트로 반환되는 처리된 데이터
- DelayConfig: 지연 시나리오 설정 정보

## API 및 인터페이스

### REST API 엔드포인트

- POST /api/image: 이미지 업로드 및 처리 요청
  - 요청 본문: Data::Image 객체
  - 응답: Data::PosePacket 객체
- GET /api/delay/config: 현재 지연 설정 조회
  - 응답: DelayConfig 객체
- POST /api/delay/config: 지연 설정 변경
  - 요청 본문: DelayConfig 객체
  - 응답: 성공/실패 상태

### 내부 API

- DelaySimulator.applyDelay(milliseconds): 지정된 시간만큼 지연 적용
- DelaySimulator.setStrategy(strategyType, params): 지연 전략 설정
- ImageProcessor.process(image): 이미지 처리 및 결과 데이터 생성

## 기술 스택

- 언어: Python
- 프레임워크: Flask (REST API 서버)
- 라이브러리: 
  - NumPy, OpenCV (이미지 처리)
  - Requests (HTTP 클라이언트)
  - PyTest (테스트)
- 도구: 
  - Postman (API 테스트)
  - Docker (컨테이너화)
