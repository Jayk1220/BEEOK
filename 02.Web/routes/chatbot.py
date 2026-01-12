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



# ------------------------------------------
#  내부 데이터 처리 (메모 요약, 어제 하루 요약)
# ------------------------------------------

def customer_summary(customer_id):
    """AI reads memos and summarizes them.
    analyze each customer's purchase history and summarize it.
    """

    # 메모 가져오기
    with engine.connect() as conn:
        # SQL
        memo_query = text("SELECT MEMO_TEXT FROM CUSTOMER_MEMO WHERE CUSTOMER_ID = :cid ORDER BY DATE DESC")
        memos = conn.execute(memo_query, {"cid": customer_id}).fetchall()
        memo_context = "\n".join([f"- {m[0]}" for m in memos])

    # 구매 패턴 분석

    # AI prompt
    prompt = f"""
    you are a professional assistant who is in charge of customer management.
    review following memos and purchase history of a customer and analyze it.
    the user only speaks Korean so please answer in korean.

    [memos]: {memo_context}
    [purchase history]: {p_context}
    
    summary:
    """
    response = ollama.chat(model='exaone3.5:7.8b', messages=[{'role': 'user', 'content': prompt}])
    summary = response['message']['content'].strip()
    
    # DB update
    with engine.begin() as update_conn:
        update_conn.execute(text("""
            UPDATE CUSTOMER SET MEMO = :summary, SUMMARY_TIME = CURRENT_TIMESTAMP WHERE CUSTOMER_ID = :cid
        """), {"summary": summary, "cid": customer_id})
# ------------------------------------------
#  RAG
# ------------------------------------------


