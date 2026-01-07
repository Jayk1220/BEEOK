import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from extensions import db, login_manager, migrate
from auth import auth_bp
from models import User


load_dotenv('../.env')
def create_app():
    app = Flask(__name__)

    # db 연결
    # MariaDB 설정 (3307 포트)
    db_user = os.environ.get('DB_USER')
    db_pw = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3307')
    db_name = os.environ.get('DB_NAME')
    db_secret_key = os.environ.get('DB_SECRET_KEY')
    # MariaDB 연동 URI
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}'
        '?charset=utf8mb4'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = f"{db_secret_key}"


    db.init_app(app)
    login_manager.init_app(app)

    # -------------------
    # 블루프린트 추가
    # -------------------

    # 로그인
    app.register_blueprint(auth_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    # 1. 로그인 성공 후 대시보드로 이동
    @app.route('/dashboard')
    def dashboard():
        return "<h1>로그인 성공</h1>"

    return app
    # -------------------
    # 실행
    # -------------------
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)