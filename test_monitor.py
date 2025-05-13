import requests
import json
import time
import random

# 서버 URL
SERVER_URL = "http://localhost:5000/api/image"

# 테스트 데이터 생성 함수
def create_test_data():
    # 이미지 ID 생성 (랜덤)
    image_id = random.randint(1, 10000)
    
    # 타임스탬프 생성 (현재 시간을 나노초로 변환)
    timestamp_ns = int(time.time() * 1_000_000_000)
    
    # 테스트 데이터 생성
    test_data = {
        "ID": {
            "imageID": image_id,
            "shipID": 1,
            "UserID": 1,
            "cameraId": 0
        },
        "timestamp_ns": timestamp_ns,
        "camera": {
            "width": 1920,
            "height": 1080,
            "format": "jpeg",
            "focal_px": [1000.0, 1000.0],
            "principal_px": [960.0, 540.0],
            "exposure_us": 10000,
            "iso": 100
        },
        "pose": {
            "position_m": [
                random.uniform(-10.0, 10.0),
                random.uniform(-10.0, 10.0),
                random.uniform(-10.0, 10.0)
            ],
            "quaternion": [0.0, 0.0, 0.0, 1.0],
            "zone": {
                "deck": 1,
                "compartment": "Main",
                "zone_id": 1
            }
        },
        "image": "base64_encoded_image_data_placeholder"
    }
    
    return test_data

# 테스트 데이터 전송 함수
def send_test_data(data):
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(SERVER_URL, json=data, headers=headers)
        
        if response.status_code == 200:
            print(f"데이터 전송 성공: {response.status_code}")
            print(f"응답 데이터: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"데이터 전송 실패: {response.status_code}")
            print(f"오류 메시지: {response.text}")
            return False
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False

# 메인 함수
def main():
    print("데이터 송수신 모니터링 테스트 시작")
    
    # 테스트 횟수
    test_count = 10
    
    for i in range(test_count):
        print(f"\n테스트 {i+1}/{test_count}")
        
        # 테스트 데이터 생성
        test_data = create_test_data()
        
        # 테스트 데이터 전송
        success = send_test_data(test_data)
        
        if not success:
            print("테스트 중단")
            break
        
        # 1초 대기
        time.sleep(1)
    
    print("\n데이터 송수신 모니터링 테스트 완료")

if __name__ == "__main__":
    main()
