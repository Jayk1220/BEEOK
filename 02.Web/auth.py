from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_user, logout_user, current_user
from extensions import db
from models import User

# bp 이름 auth

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST']) #로그인 관련
def login():
    # 로그인 된 상태 --> dashboard 보내기
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # 로그인 버튼 눌렀을 경우
    if request.method == 'POST':
        login_id = request.form.get('login_id')
        password = request.form.get('password')

        # DB에서 아이디 찾기
        user = User.query.filter_by(login_id=login_id).first()
        
        # 비밀번호 대조 ==> 암호화는 하지 않음
        if user and user.password == password:
            login_user(user) #true면 login
            return redirect(url_for('dashboard')) #dashboard로 보내기
        
        else: # 실패시
            flash('아이디 또는 비밀번호를 다시 확인해주세요.')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET', 'POST']) #로그아웃 관련
def logout():
    logout_user() # 로그아웃
    return redirect(url_for('auth.login'))