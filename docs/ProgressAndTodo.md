# 진행 상황 및 할 일

이 문서는 프로젝트의 진행 상황과 앞으로 해야 할 일들을 관리합니다.

## 진행 상황

### 완료된 작업

- [x] 프로젝트 초기 설정
  - [x] 가상환경 설정
  - [x] 기본 폴더 구조 생성
  - [x] 문서 파일 생성
- [x] 프로젝트 문서화
  - [x] 사용자 요구사항 정리
  - [x] 프로젝트 설명 문서 작성
  - [x] 진행 상황 및 할 일 문서 업데이트
  - [x] README.md 작성
- [x] 가상환경 활성화 스크립트 생성
  - [x] activate.sh 스크립트 생성
  - [x] .bash_aliases 파일 생성
- [x] REST API 서버 구현
  - [x] 기본 서버 구조 설정
  - [x] 이미지 처리 API 구현
  - [x] 지연 시뮬레이터 구현
- [x] 프로젝트 기본 구조 설정
  - [x] 필요한 패키지 설치
  - [x] 기본 디렉토리 구조 생성
  - [x] 설정 파일 생성
- [x] 지연 시뮬레이터 구현
  - [x] 지연 전략 인터페이스 정의
  - [x] 다양한 지연 전략 구현
  - [x] 지연 설정 관리 기능 구현
- [x] 이미지 처리 모듈 구현
  - [x] 이미지 데이터 파싱
  - [x] 간단한 이미지 처리 기능 구현
  - [x] PosePacket 데이터 생성
- [x] 테스트 코드 작성
  - [x] API 테스트
  - [x] 지연 시뮬레이터 테스트
- [x] 데이터 모델 업데이트
  - [x] 유니티 앱의 Data::Image 구조 구현 (FramePacket)
  - [x] 유니티 앱의 Data::PosePacket 구조 구현
  - [x] 이미지 처리 서비스 업데이트
  - [x] API 응답에 도착/출발 시간 추가
- [x] 지연 시나리오 엔드포인트 추가
  - [x] 각 지연 전략별 전용 엔드포인트 구현
  - [x] 테스트 시나리오별 간편 엔드포인트 구현
  - [x] API 문서 업데이트
- [x] 모니터링 기능 추가
  - [x] 지연 시나리오 프로파일 그래프 시각화
  - [x] 최근 요청 모니터링 페이지 구현
  - [x] 실시간 업데이트 기능 추가

### 진행 중인 작업

- [ ] 서버 테스트 및 개선
  - [ ] 실제 유니티 앱과의 연동 테스트
  - [ ] 성능 최적화
  - [ ] 오류 처리 개선

## 할 일 목록

### 우선순위 높음

- [ ] 서버 테스트 및 개선
  - [ ] 실제 유니티 앱과의 연동 테스트
  - [ ] 다양한 이미지 형식 지원
  - [ ] 오류 처리 개선
- [ ] 지연 시나리오 테스트
  - [ ] 각 시나리오별 테스트 케이스 작성
  - [ ] 시나리오 전환 테스트
  - [ ] 장시간 실행 안정성 테스트

### 우선순위 중간

- [ ] 추가 기능 구현
  - [ ] 로깅 기능 강화
  - [ ] 모니터링 대시보드 구현
  - [ ] 설정 파일을 통한 서버 구성 관리
- [ ] 문서화 개선
  - [ ] API 문서 상세화
  - [ ] 사용 사례 및 예제 추가
  - [ ] 트러블슈팅 가이드 작성

### 우선순위 낮음

- [ ] 배포 및 운영 환경 설정
  - [ ] Docker 컨테이너화
  - [ ] CI/CD 파이프라인 구성
  - [ ] 모니터링 및 알림 설정
- [ ] 추가 테스트 시나리오 개발
  - [ ] 네트워크 패킷 손실 시뮬레이션
  - [ ] 대역폭 제한 시뮬레이션
  - [ ] 서버 재시작 시뮬레이션

## 이슈 및 해결 방안

### 현재 이슈

- 실제 유니티 앱과의 연동: 실제 유니티 앱에서 사용하는 데이터 형식과 서버에서 구현한 형식의 호환성 확인 필요
  - 해결 방안: 유니티 앱 개발자와 협력하여 데이터 형식 조정 및 테스트 진행

### 해결된 이슈

- 데이터 모델 정의: Data::Image와 Data::PosePacket의 정확한 구조가 명확하지 않음
  - 해결 방법: 유니티 앱 개발자로부터 정확한 데이터 구조를 제공받아 FramePacket과 PosePacket 클래스로 구현
- 시간 정보 처리: 요청 도착 시간과 응답 출발 시간 기록 필요
  - 해결 방법: PosePacket에 time_stamps 필드 추가하여 [time_arrive, time_depart] 형식으로 시간 정보 저장
- 가상환경 활성화: 가상환경을 쉽게 활성화할 수 있는 방법 필요
  - 해결 방법: activate.sh 스크립트와 .bash_aliases 파일을 생성하여 'activate' 명령어로 가상환경 활성화 가능

## 다음 마일스톤

- 서버 안정화 및 최적화: (목표 날짜: 1주일 이내)
  - 실제 유니티 앱과의 연동 테스트 완료
  - 성능 최적화 및 오류 처리 개선
  - 추가 로깅 및 모니터링 기능 구현
- 운영 환경 구성: (목표 날짜: 2주일 이내)
  - Docker 컨테이너화
  - CI/CD 파이프라인 구성
  - 운영 환경 문서화 완료
