"""
API 테스트
"""

import json
import base64
import pytest
from app import create_app

@pytest.fixture
def client():
    """
    테스트 클라이언트 생성
    """
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

def test_upload_image(client):
    """
    이미지 업로드 API 테스트
    """
    # 테스트용 이미지 데이터 생성 (1x1 픽셀 검은색 이미지)
    image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # 요청 데이터 생성
    data = {
        'image_data': base64.b64encode(image_data).decode('utf-8'),
        'metadata': {
            'id': 'test-image-1',
            'timestamp': 1620000000.0
        }
    }
    
    # API 요청
    response = client.post(
        '/api/image',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    # 응답 확인
    assert response.status_code == 200
    
    # 응답 데이터 확인
    response_data = json.loads(response.data)
    assert 'pose_data' in response_data
    assert 'timestamp' in response_data
    assert 'metadata' in response_data
    
    # 포즈 데이터 확인
    pose_data = response_data['pose_data']
    assert 'position' in pose_data
    assert 'rotation' in pose_data
    assert 'confidence' in pose_data

def test_get_delay_config(client):
    """
    지연 설정 조회 API 테스트
    """
    # API 요청
    response = client.get('/api/delay/config')
    
    # 응답 확인
    assert response.status_code == 200
    
    # 응답 데이터 확인
    response_data = json.loads(response.data)
    assert 'strategy' in response_data
    assert 'params' in response_data

def test_set_delay_config(client):
    """
    지연 설정 변경 API 테스트
    """
    # 요청 데이터 생성
    data = {
        'strategy': 'FixedDelayStrategy',
        'params': {
            'delay_seconds': 0.1
        }
    }
    
    # API 요청
    response = client.post(
        '/api/delay/config',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    # 응답 확인
    assert response.status_code == 200
    
    # 설정이 변경되었는지 확인
    response = client.get('/api/delay/config')
    response_data = json.loads(response.data)
    
    assert response_data['strategy'] == 'FixedDelayStrategy'
    assert response_data['params']['delay_seconds'] == 0.1
