from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# DB객체 생성
db = SQLAlchemy()

# 로그인 관리 생성
login_manager = LoginManager()

# DB변경 관리
migrate = Migrate()



# -------------------
# login 설정
# -------------------

# 비로그인 접속시 로그인페이지로 이동
login_manager.login_view = 'auth.login'

# 로그인 안내메시지
login_manager.login_message = '로그인 해주세요'

# 로그인 정보 로드 함수 
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
