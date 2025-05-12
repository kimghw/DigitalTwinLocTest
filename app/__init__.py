from flask import Flask

def create_app():
    """
    Flask 애플리케이션 팩토리 함수
    """
    app = Flask(__name__)
    
    # API 라우트 등록
    from app.api import routes
    app.register_blueprint(routes.api_bp)
    
    # 루트 라우트 등록
    app.register_blueprint(routes.root_bp)
    
    return app
