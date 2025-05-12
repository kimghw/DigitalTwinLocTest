import time
import base64
import numpy as np
import cv2
from app.models.frame_packet import FramePacket, IdBlock, CameraBlock, PoseBlock, ZoneBlock
from app.models.pose_packet import PosePacket

def process_image(image_data):
    """
    이미지 데이터를 처리하고 PosePacket 객체를 생성
    
    Args:
        image_data (dict): 이미지 데이터를 포함한 딕셔너리
        
    Returns:
        dict: PosePacket 데이터를 포함한 딕셔너리
    """
    # 이미지 객체 생성 (기존 형식 또는 새 형식 모두 지원)
    if 'image' in image_data:
        # 새 형식 (FramePacket)
        frame_packet = FramePacket.from_dict(image_data)
        image_bytes = frame_packet.get_image_bytes()
        id_block = frame_packet.ID
        timestamp_ns = frame_packet.timestamp_ns
        input_pose = frame_packet.pose  # 입력 포즈 데이터
    else:
        # 기존 형식 (이전 버전과의 호환성 유지)
        image_bytes = _get_image_bytes_from_legacy_format(image_data)
        id_block = _create_id_block_from_legacy_format(image_data)
        timestamp_ns = int(time.time() * 1_000_000_000)  # 현재 시간을 나노초로 변환
        input_pose = None
    
    # 이미지 처리 (실제 구현에서는 더 복잡한 처리가 필요할 수 있음)
    pose_block = _extract_pose_data(image_bytes, input_pose)
    
    # PosePacket 객체 생성
    pose_packet = PosePacket(
        ID=id_block,
        timestamp_ns=timestamp_ns,
        pose=pose_block
    )
    
    # 도착 시간 설정 (서버에서 요청을 받은 시간)
    pose_packet.set_arrival_time()
    
    # 지연 시뮬레이션 후 출발 시간 설정은 API 라우트에서 처리
    
    # 딕셔너리로 변환하여 반환
    return pose_packet.to_dict()

def _get_image_bytes_from_legacy_format(image_data):
    """
    기존 형식의 이미지 데이터에서 바이트 배열 추출
    
    Args:
        image_data (dict): 기존 형식의 이미지 데이터
        
    Returns:
        bytes: 이미지 바이트 배열
    """
    image_data_str = image_data.get('image_data', '')
    if not image_data_str:
        return b''
    
    if isinstance(image_data_str, str):
        try:
            # Base64 디코딩 시도
            return base64.b64decode(image_data_str)
        except Exception:
            try:
                # Hex 디코딩 시도
                return bytes.fromhex(image_data_str)
            except Exception:
                return b''
    elif isinstance(image_data_str, bytes):
        return image_data_str
    else:
        return b''

def _create_id_block_from_legacy_format(image_data):
    """
    기존 형식의 이미지 데이터에서 IdBlock 생성
    
    Args:
        image_data (dict): 기존 형식의 이미지 데이터
        
    Returns:
        IdBlock: 생성된 IdBlock 객체
    """
    metadata = image_data.get('metadata', {})
    return IdBlock(
        imageID=metadata.get('id', 0) if isinstance(metadata.get('id'), int) else 0,
        shipID=metadata.get('shipID', 0),
        UserID=metadata.get('UserID', 0),
        cameraId=metadata.get('cameraId', 0)
    )

def _extract_pose_data(image_bytes, input_pose=None):
    """
    이미지에서 포즈 데이터 추출 및 랜덤 변형 적용
    
    Args:
        image_bytes (bytes): 처리할 이미지 바이트 배열
        input_pose (PoseBlock, optional): 입력 포즈 데이터
        
    Returns:
        PoseBlock: 추출된 포즈 데이터
    """
    # 기본 영역 정보 생성
    zone = ZoneBlock(
        deck=1,
        compartment="Main",
        zone_id=1
    )
    
    # 입력 포즈 데이터가 있는 경우 해당 영역 정보 사용
    if input_pose and hasattr(input_pose, 'zone'):
        zone = input_pose.zone
    
    # 이미지 데이터가 없는 경우 기본값 반환
    if not image_bytes:
        return PoseBlock(
            position_m=[0.0, 0.0, 0.0],
            quaternion=[0.0, 0.0, 0.0, 1.0],
            zone=zone
        )
    
    try:
        # 이미지 데이터를 NumPy 배열로 변환
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 기본 위치 및 회전 설정
        position_m = [0.0, 0.0, 0.0]
        quaternion = [0.0, 0.0, 0.0, 1.0]
        
        # 입력 포즈 데이터가 있는 경우 해당 값을 기준으로 사용
        if input_pose:
            if hasattr(input_pose, 'position_m') and input_pose.position_m:
                position_m = input_pose.position_m.copy()
            if hasattr(input_pose, 'quaternion') and input_pose.quaternion:
                quaternion = input_pose.quaternion.copy()
        
        # 랜덤 변형 적용 (1미터 내부에서 위치 변경)
        import random
        
        # 위치에 랜덤 오프셋 적용 (최대 1미터)
        position_m[0] += random.uniform(-1.0, 1.0)
        position_m[1] += random.uniform(-1.0, 1.0)
        position_m[2] += random.uniform(-1.0, 1.0)
        
        # 회전에 랜덤 변형 적용
        # 쿼터니언 값에 작은 랜덤 변화 적용 (단순화된 방식)
        for i in range(3):  # x, y, z 성분에 랜덤 변화 적용
            quaternion[i] += random.uniform(-0.1, 0.1)
        
        # 쿼터니언 정규화 (단위 쿼터니언 유지)
        magnitude = sum(q*q for q in quaternion) ** 0.5
        if magnitude > 0:
            quaternion = [q/magnitude for q in quaternion]
        
        return PoseBlock(
            position_m=position_m,
            quaternion=quaternion,
            zone=zone
        )
    
    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {str(e)}")
        
        # 오류 발생 시 기본값 반환
        return PoseBlock(
            position_m=[0.0, 0.0, 0.0],
            quaternion=[0.0, 0.0, 0.0, 1.0],
            zone=zone
        )
