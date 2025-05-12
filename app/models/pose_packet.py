"""
Data::PosePacket 모델 클래스

서버에서 클라이언트로 반환되는 처리된 데이터를 표현
"""

import time
from app.models.frame_packet import IdBlock, PoseBlock

class PosePacket:
    """
    PosePacket 클래스
    
    서버에서 클라이언트로 반환되는 처리된 데이터를 표현
    """
    
    def __init__(self, ID=None, timestamp_ns=0, time_stamps=None, pose=None):
        """
        PosePacket 객체 초기화
        
        Args:
            ID (IdBlock): 식별 정보
            timestamp_ns (long): 타임스탬프 (나노초)
            time_stamps (list): [time_arrive, time_depart] 시간 정보
            pose (PoseBlock): 위치 및 자세 정보
        """
        self.ID = ID or IdBlock()
        self.timestamp_ns = timestamp_ns
        self.time_stamps = time_stamps or [0, 0]  # [time_arrive, time_depart]
        self.pose = pose or PoseBlock()
    
    @classmethod
    def from_dict(cls, data):
        """
        딕셔너리에서 PosePacket 객체 생성
        
        Args:
            data (dict): PosePacket 데이터를 포함한 딕셔너리
            
        Returns:
            PosePacket: 생성된 PosePacket 객체
        """
        if not data:
            return cls()
        
        return cls(
            ID=IdBlock.from_dict(data.get('ID', {})),
            timestamp_ns=data.get('timestamp_ns', 0),
            time_stamps=data.get('time_stamps', [0, 0]),
            pose=PoseBlock.from_dict(data.get('pose', {}))
        )
    
    def to_dict(self):
        """
        PosePacket 객체를 딕셔너리로 변환
        
        Returns:
            dict: PosePacket 데이터를 포함한 딕셔너리
        """
        return {
            'ID': self.ID.to_dict(),
            'timestamp_ns': self.timestamp_ns,
            'time_stamps': self.time_stamps,
            'pose': self.pose.to_dict()
        }
    
    def set_arrival_time(self):
        """
        도착 시간 설정 (서버에서 요청을 받은 시간)
        """
        self.time_stamps[0] = int(time.time() * 1_000_000_000)  # 현재 시간을 나노초로 변환
    
    def set_departure_time(self):
        """
        출발 시간 설정 (서버에서 응답을 보내는 시간)
        """
        self.time_stamps[1] = int(time.time() * 1_000_000_000)  # 현재 시간을 나노초로 변환
