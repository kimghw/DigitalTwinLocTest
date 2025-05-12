"""
애플리케이션 설정 파일
"""

class Config:
    """
    기본 설정 클래스
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'digital-twin-loc-test-secret-key'
    
    # 서버 설정
    HOST = '0.0.0.0'
    PORT = 5000
    
    # 로깅 설정
    LOG_LEVEL = 'INFO'
    
    # 기본 지연 설정
    DEFAULT_DELAY_STRATEGY = 'FixedDelayStrategy'
    DEFAULT_DELAY_PARAMS = {'delay_seconds': 0.0}  # 기본값: 지연 없음

class DevelopmentConfig(Config):
    """
    개발 환경 설정
    """
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """
    테스트 환경 설정
    """
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """
    운영 환경 설정
    """
    # 운영 환경에서는 보안을 위해 환경 변수에서 비밀 키를 가져오는 것이 좋음
    # SECRET_KEY = os.environ.get('SECRET_KEY', 'digital-twin-loc-test-secret-key')
    pass

# 환경별 설정 매핑
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """
    설정 객체 반환
    
    Args:
        config_name (str, optional): 설정 이름
        
    Returns:
        Config: 설정 객체
    """
    return config.get(config_name or 'default')
