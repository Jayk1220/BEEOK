# model : 'exaone3.5:7.8b'

import ollama
from flask import Blueprint, request, jsonify
from flask_login import login_required

# 1. 블루프린트 정의
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api')

def chatbot(user_msg):
    try:
        response = ollama.chat(model='exaone3.5:7.8b', messages=[
            {
                'role': 'system',
                'content': (
                    """
                    you are a professional business assistant who is dealing with a person who can only speak Korean.
                    your name is BEEOK AI.
                    Answer questions in Korean.
                    """
                )
            },
            {'role': 'user', 'content': user_msg},
        ])
        return response['message']['content']
    except Exception as e:
        return f"챗봇 응답 중 오류가 발생했습니다: {str(e)}"
    
@chatbot_bp.route('/chat', methods=['POST'])
def chat_api():
    # 클라이언트(JS) 데이터 받기
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "메시지가 없습니다."}), 400
        
    # AI 답변 생성
    bot_response = chatbot(user_message)
    
    # 결과를 다시 브라우저로 전송
    return jsonify({"reply": bot_response})
