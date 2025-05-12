"""
Data::Image 모델 클래스

유니티 앱에서 서버로 전송되는 이미지 데이터를 표현
"""

import base64
import json

class IdBlock:
    """
    IdBlock 클래스
    
    이미지 식별 정보를 포함
    """
    
    def __init__(self, imageID=0, shipID=0, UserID=0, cameraId=0):
        """
        IdBlock 객체 초기화
        
        Args:
            imageID (int): 이미지 ID
            shipID (int): 선박 ID
            UserID (int): 사용자 ID
            cameraId (int): 카메라 ID
        """
        self.imageID = imageID
        self.shipID = shipID
        self.UserID = UserID
        self.cameraId = cameraId
    
    @classmethod
    def from_dict(cls, data):
        """
        딕셔너리에서 IdBlock 객체 생성
        
        Args:
            data (dict): IdBlock 데이터를 포함한 딕셔너리
            
        Returns:
            IdBlock: 생성된 IdBlock 객체
        """
        if not data:
            return cls()
        
        return cls(
            imageID=data.get('imageID', 0),
            shipID=data.get('shipID', 0),
            UserID=data.get('UserID', 0),
            cameraId=data.get('cameraId', 0)
        )
    
    def to_dict(self):
        """
        IdBlock 객체를 딕셔너리로 변환
        
        Returns:
            dict: IdBlock 데이터를 포함한 딕셔너리
        """
        return {
            'imageID': self.imageID,
            'shipID': self.shipID,
            'UserID': self.UserID,
            'cameraId': self.cameraId
        }


class CameraBlock:
    """
    CameraBlock 클래스
    
    카메라 정보를 포함
    """
    
    def __init__(self, width=0, height=0, format="jpeg", focal_px=None, principal_px=None, exposure_us=0, iso=0):
        """
        CameraBlock 객체 초기화
        
        Args:
            width (int): 이미지 너비
            height (int): 이미지 높이
            format (str): 이미지 형식 ("jpeg", "png" 등)
            focal_px (list): 초점 거리 (픽셀 단위, 길이 2)
            principal_px (list): 주점 좌표 (픽셀 단위, 길이 2)
            exposure_us (int): 노출 시간 (마이크로초)
            iso (int): ISO 값
        """
        self.width = width
        self.height = height
        self.format = format
        self.focal_px = focal_px or [0.0, 0.0]
        self.principal_px = principal_px or [0.0, 0.0]
        self.exposure_us = exposure_us
        self.iso = iso
    
    @classmethod
    def from_dict(cls, data):
        """
        딕셔너리에서 CameraBlock 객체 생성
        
        Args:
            data (dict): CameraBlock 데이터를 포함한 딕셔너리
            
        Returns:
            CameraBlock: 생성된 CameraBlock 객체
        """
        if not data:
            return cls()
        
        return cls(
            width=data.get('width', 0),
            height=data.get('height', 0),
            format=data.get('format', "jpeg"),
            focal_px=data.get('focal_px', [0.0, 0.0]),
            principal_px=data.get('principal_px', [0.0, 0.0]),
            exposure_us=data.get('exposure_us', 0),
            iso=data.get('iso', 0)
        )
    
    def to_dict(self):
        """
        CameraBlock 객체를 딕셔너리로 변환
        
        Returns:
            dict: CameraBlock 데이터를 포함한 딕셔너리
        """
        return {
            'width': self.width,
            'height': self.height,
            'format': self.format,
            'focal_px': self.focal_px,
            'principal_px': self.principal_px,
            'exposure_us': self.exposure_us,
            'iso': self.iso
        }


class ZoneBlock:
    """
    ZoneBlock 클래스
    
    위치 영역 정보를 포함
    """
    
    def __init__(self, deck=0, compartment="", zone_id=0):
        """
        ZoneBlock 객체 초기화
        
        Args:
            deck (int): 데크 번호
            compartment (str): 구획 정보
            zone_id (int): 영역 ID
        """
        self.deck = deck
        self.compartment = compartment
        self.zone_id = zone_id
    
    @classmethod
    def from_dict(cls, data):
        """
        딕셔너리에서 ZoneBlock 객체 생성
        
        Args:
            data (dict): ZoneBlock 데이터를 포함한 딕셔너리
            
        Returns:
            ZoneBlock: 생성된 ZoneBlock 객체
        """
        if not data:
            return cls()
        
        return cls(
            deck=data.get('deck', 0),
            compartment=data.get('compartment', ""),
            zone_id=data.get('zone_id', 0)
        )
    
    def to_dict(self):
        """
        ZoneBlock 객체를 딕셔너리로 변환
        
        Returns:
            dict: ZoneBlock 데이터를 포함한 딕셔너리
        """
        return {
            'deck': self.deck,
            'compartment': self.compartment,
            'zone_id': self.zone_id
        }


class PoseBlock:
    """
    PoseBlock 클래스
    
    위치 및 자세 정보를 포함
    """
    
    def __init__(self, position_m=None, quaternion=None, zone=None):
        """
        PoseBlock 객체 초기화
        
        Args:
            position_m (list): 위치 좌표 (미터 단위)
            quaternion (list): 쿼터니언 (회전)
            zone (ZoneBlock): 영역 정보
        """
        self.position_m = position_m or [0.0, 0.0, 0.0]
        self.quaternion = quaternion or [0.0, 0.0, 0.0, 1.0]
        self.zone = zone or ZoneBlock()
    
    @classmethod
    def from_dict(cls, data):
        """
        딕셔너리에서 PoseBlock 객체 생성
        
        Args:
            data (dict): PoseBlock 데이터를 포함한 딕셔너리
            
        Returns:
            PoseBlock: 생성된 PoseBlock 객체
        """
        if not data:
            return cls()
        
        return cls(
            position_m=data.get('position_m', [0.0, 0.0, 0.0]),
            quaternion=data.get('quaternion', [0.0, 0.0, 0.0, 1.0]),
            zone=ZoneBlock.from_dict(data.get('zone', {}))
        )
    
    def to_dict(self):
        """
        PoseBlock 객체를 딕셔너리로 변환
        
        Returns:
            dict: PoseBlock 데이터를 포함한 딕셔너리
        """
        return {
            'position_m': self.position_m,
            'quaternion': self.quaternion,
            'zone': self.zone.to_dict()
        }


class FramePacket:
    """
    FramePacket 클래스 (Data::Image)
    
    유니티 앱에서 서버로 전송되는 이미지 데이터를 표현
    """
    
    def __init__(self, ID=None, timestamp_ns=0, camera=None, pose=None, image=""):
        """
        FramePacket 객체 초기화
        
        Args:
            ID (IdBlock): 식별 정보
            timestamp_ns (long): 타임스탬프 (나노초)
            camera (CameraBlock): 카메라 정보
            pose (PoseBlock): 위치 및 자세 정보
            image (str): Base64 또는 Hex 인코딩된 이미지 데이터
        """
        self.ID = ID or IdBlock()
        self.timestamp_ns = timestamp_ns
        self.camera = camera or CameraBlock()
        self.pose = pose or PoseBlock()
        self.image = image
    
    @classmethod
    def from_dict(cls, data):
        """
        딕셔너리에서 FramePacket 객체 생성
        
        Args:
            data (dict): FramePacket 데이터를 포함한 딕셔너리
            
        Returns:
            FramePacket: 생성된 FramePacket 객체
        """
        if not data:
            return cls()
        
        return cls(
            ID=IdBlock.from_dict(data.get('ID', {})),
            timestamp_ns=data.get('timestamp_ns', 0),
            camera=CameraBlock.from_dict(data.get('camera', {})),
            pose=PoseBlock.from_dict(data.get('pose', {})),
            image=data.get('image', "")
        )
    
    def to_dict(self):
        """
        FramePacket 객체를 딕셔너리로 변환
        
        Returns:
            dict: FramePacket 데이터를 포함한 딕셔너리
        """
        return {
            'ID': self.ID.to_dict(),
            'timestamp_ns': self.timestamp_ns,
            'camera': self.camera.to_dict(),
            'pose': self.pose.to_dict(),
            'image': self.image
        }
    
    def get_image_bytes(self):
        """
        이미지 데이터를 바이트 배열로 변환
        
        Returns:
            bytes: 디코딩된 이미지 데이터
        """
        if not self.image:
            return b''
        
        try:
            # Base64 디코딩 시도
            return base64.b64decode(self.image)
        except Exception:
            try:
                # Hex 디코딩 시도
                return bytes.fromhex(self.image)
            except Exception:
                return b''
