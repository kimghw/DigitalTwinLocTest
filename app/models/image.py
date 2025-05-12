class Image:
    """
    Data::Image 클래스
    
    유니티 앱에서 서버로 전송되는 이미지 데이터를 표현
    """
    
    def __init__(self, image_data=None, metadata=None):
        """
        이미지 객체 초기화
        
        Args:
            image_data (bytes, optional): 이미지 바이너리 데이터
            metadata (dict, optional): 이미지 관련 메타데이터
        """
        self.image_data = image_data or b''
        self.metadata = metadata or {}
    
    @classmethod
    def from_dict(cls, data):
        """
        딕셔너리에서 Image 객체 생성
        
        Args:
            data (dict): 이미지 데이터를 포함한 딕셔너리
            
        Returns:
            Image: 생성된 Image 객체
        """
        if not data:
            return cls()
            
        # 이미지 데이터가 base64 인코딩된 문자열인 경우 처리
        image_data = data.get('image_data', b'')
        if isinstance(image_data, str):
            import base64
            try:
                image_data = base64.b64decode(image_data)
            except Exception:
                image_data = b''
        
        return cls(
            image_data=image_data,
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self):
        """
        Image 객체를 딕셔너리로 변환
        
        Returns:
            dict: 이미지 데이터를 포함한 딕셔너리
        """
        import base64
        
        return {
            'image_data': base64.b64encode(self.image_data).decode('utf-8') if self.image_data else '',
            'metadata': self.metadata
        }
