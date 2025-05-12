"""
애플리케이션 실행 파일
"""

import os
import logging
from app import create_app
from config import get_config

# 환경 설정 로드
config_name = os.environ.get('FLASK_ENV', 'development')
config = get_config(config_name)

# 애플리케이션 생성
app = create_app()

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    # 애플리케이션 실행
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
