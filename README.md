# DigitalTwinLocTest

유니티 앱에서 서버로 이미지를 전송하고 그 이미지에서 추출한 데이터를 다시 수신 받는 테스트를 위한 REST API 서버입니다. 다양한 지연 시나리오를 시뮬레이션하여 클라이언트 앱의 버퍼 안정성을 테스트할 수 있습니다.

## 기능

- 이미지 업로드 및 처리 API
- 다양한 지연 시나리오 시뮬레이션
  - 고정 지연
  - 점진적 증가 지연
  - 점진적 감소 지연
  - 계단식 지연
  - 무응답 시뮬레이션
  - 랜덤 지연
- 실시간 모니터링 기능
  - 지연 시나리오 프로파일 그래프 시각화
  - 최근 요청 모니터링 페이지
  - 실시간 업데이트
- 테스트 스크립트
  - 시나리오별 테스트 자동화
  - 샘플링 테스트 (1초에 1개씩 최대 100개)

## 설치 및 실행

### 요구사항

- Python 3.8 이상
- 가상환경 (venv)

### 설치

1. 가상환경 활성화:

```bash
# 가상환경 활성화
source activate.sh
```

2. 필요한 패키지 설치:

```bash
pip install flask numpy opencv-python requests pytest
```

### 실행

```bash
# 서버 실행
python run.py
```

기본적으로 서버는 `http://0.0.0.0:5000`에서 실행됩니다.

## API 사용법

### 이미지 업로드 및 처리

```
POST /api/image
```

**요청 본문**:

```json
{
  "image_data": "base64로 인코딩된 이미지 데이터",
  "metadata": {
    "id": "이미지 ID",
    "timestamp": 1620000000.0
  }
}
```

**응답**:

```json
{
  "pose_data": {
    "position": {
      "x": 0.5,
      "y": 0.5,
      "z": 0.0
    },
    "rotation": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.0,
      "w": 1.0
    },
    "confidence": 0.75
  },
  "timestamp": 1620000001.0,
  "metadata": {
    "source_image_id": "이미지 ID",
    "processing_info": "Processed by DigitalTwinLocTest server"
  }
}
```

### 지연 설정 조회

```
GET /api/delay/config
```

**응답**:

```json
{
  "strategy": "FixedDelayStrategy",
  "params": {
    "delay_seconds": 1.0
  }
}
```

### 지연 설정 변경

```
POST /api/delay/config
```

**요청 본문**:

```json
{
  "strategy": "FixedDelayStrategy",
  "params": {
    "delay_seconds": 1.0
  }
}
```

**응답**:

```json
{
  "message": "지연 설정이 변경되었습니다."
}
```

## 지연 시나리오

### 1. 고정 지연

```json
{
  "strategy": "FixedDelayStrategy",
  "params": {
    "delay_seconds": 1.0
  }
}
```

### 2. 점진적 증가 지연

```json
{
  "strategy": "ProgressiveIncreaseDelayStrategy",
  "params": {
    "initial_delay": 0.0,
    "increment": 0.5,
    "interval": 5.0,
    "max_steps": 10
  }
}
```

### 3. 점진적 감소 지연

```json
{
  "strategy": "ProgressiveDecreaseDelayStrategy",
  "params": {
    "initial_delay": 5.0,
    "decrement": 0.5,
    "interval": 5.0,
    "min_delay": 0.0
  }
}
```

### 4. 계단식 지연

```json
{
  "strategy": "StepDelayStrategy",
  "params": {
    "normal_delay": 0.0,
    "high_delay": 5.0,
    "normal_duration": 5.0,
    "high_duration": 5.0,
    "step_increment": 5.0,
    "total_duration": 300.0
  }
}
```

### 5. 무응답 시뮬레이션

```json
{
  "strategy": "NoResponseDelayStrategy",
  "params": {
    "no_response_duration": 10.0
  }
}
```

### 6. 랜덤 지연

```json
{
  "strategy": "RandomDelayStrategy",
  "params": {
    "min_delay": 0.5,
    "max_delay": 5.0,
    "change_interval": 5.0,
    "total_duration": 300.0
  }
}
```

## 테스트 실행

```bash
# 테스트 실행
pytest
```

## 모니터링 기능

서버는 두 가지 모니터링 기능을 제공합니다:

1. **메인 페이지 (http://localhost:5000/)**
   - 지연 시나리오 프로파일 그래프 시각화
   - 현재 지연 전략 정보 표시
   - API 문서 제공

2. **모니터링 페이지 (http://localhost:5000/monitor)**
   - 최근 요청 및 응답 정보 실시간 모니터링
   - 요청 ID, 포즈 정보, 지연 정보 등 표시
   - 2초마다 자동 새로고침

## 테스트 스크립트

### 시나리오별 테스트

```bash
# 시나리오별 테스트 실행
./test_delay_api.sh
```

### 샘플링 테스트

```bash
# 1초에 1개씩 최대 100개까지 이미지 업로드 API 호출 테스트
./test_sampling.sh
```

## GitHub 저장소 설정

이 프로젝트를 GitHub에 올리려면 다음 단계를 따르세요:

1. Git 저장소 초기화:

```bash
git init
```

2. 파일 추가 및 커밋:

```bash
git add .
git commit -m "Initial commit"
```

3. GitHub 저장소 생성 및 연결:

```bash
# GitHub에서 새 저장소를 생성한 후
git remote add origin https://github.com/yourusername/DigitalTwinLocTest.git
git branch -M main
git push -u origin main
```

## 프로젝트 구조

```
DigitalTwinLocTest/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── image.py
│   │   ├── frame_packet.py
│   │   ├── pose_packet.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_processor.py
│   │   ├── delay_simulator.py
│   │   ├── delay_strategies.py
├── config.py
├── run.py
├── docs/
│   ├── user_requirement.md
│   ├── project_description.md
│   ├── ProgressAndTodo.md
├── test/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_delay_simulator.py
├── test_delay_api.sh
├── test_sampling.sh
├── test_frame_packet.json
├── .gitignore
├── README.md
├── activate.sh
# DigitalTwinLocTest
