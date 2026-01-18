# model : 'exaone3.5:7.8b'

import ollama
from flask import Blueprint, request, jsonify
from flask_login import login_required
from ddgs import DDGS
from datetime import datetime
import socket

# 1. 블루프린트 정의
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api')

def is_connected():
    """인터넷 연결 상태를 체크하고 자원을 안전하게 해제합니다."""
    try:
        # with 문을 사용하여 작업이 끝나면 자동으로 소켓을 닫습니다.
        with socket.create_connection(("8.8.8.8", 53), timeout=1) as sock:
            return True
    except OSError:
        return False
    
def search_web(query: str) -> str:
    """인터넷에서 최신 정보나 실시간 뉴스 검색."""
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=5)]
            return "\n".join(results)
    except Exception as e:
        return f"검색 오류: {str(e)}"

def chatbot(user_msg):
    try:
        target_model = 'exaone3.5:7.8b'
        connected = is_connected()
        now_str = datetime.now().strftime("%Y-%m-%d %A")

        tools = [{
            'type': 'function',
            'function': {
                'name': 'search_web',
                'description': '실시간 뉴스, 날씨, 주가 등 최신 정보를 검색합니다.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'query': {'type': 'string', 'description': '검색어'}
                    },
                    'required': ['query']
                }
            }
        }]

        # 페르소나 및 언어 제약 강화
        system_content = (
            f"당신은 전문 비즈니스 비서 'BEEOK AI'입니다. "
            f"현재 날짜는 {now_str}입니다. "
            f"--- 지침 ---\n"
            f"1. 반드시 한국어로만 답변하세요. 영어로 질문받아도 한국어로 답변합니다.\n"
            f"2. 비즈니스 환경에 적합한 정중하고 전문적인 말투를 사용하세요.\n"
            f"3. 최신 정보가 필요한 경우에만 search_web 도구를 호출하세요."
        )

        response = ollama.chat(
            model=target_model,
            messages=[
                {'role': 'system', 'content': system_content},
                {'role': 'user', 'content': user_msg}
            ],
            tools=tools
        )

        if response.message.tool_calls:
            if not connected:
                offline_notice = "⚠️ **현재 인터넷 연결이 오프라인 상태입니다.**\n실시간 검색이 불가능하여 제가 보유한 지식만으로 답변해 드립니다.\n\n"
                
                fallback_res = ollama.chat(
                    model=target_model,
                    messages=[
                        {'role': 'system', 'content': "당신은 BEEOK AI입니다. 반드시 한국어로만 답변하세요. 현재 오프라인 상태임을 안내하고 아는 대로 답하세요."},
                        {'role': 'user', 'content': user_msg}
                    ]
                )
                return offline_notice + fallback_res.message.content

            messages = [{'role': 'user', 'content': user_msg}, response.message]
            for tool in response.message.tool_calls:
                if tool.function.name == 'search_web':
                    query = tool.function.arguments.get('query')
                    result = search_web(query)
                    messages.append({'role': 'tool', 'content': result, 'name': tool.function.name})
            
            # 2차 생성 시에도 페르소나 재강조
            final_response = ollama.chat(
                model=target_model, 
                messages=[{'role': 'system', 'content': "당신은 BEEOK AI입니다. 검색된 정보를 바탕으로 반드시 한국어로 친절하게 답변하세요."}] + messages
            )
            return final_response.message.content
        
        return response.message.content

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
    당신은 고객 관리를 담당하는 전문 비서 'BEEOK AI'입니다.
    다음 고객의 메모와 구매 이력을 분석하여 비즈니스 요약 보고서를 작성하세요.
    반드시 한국어로 작성해야 합니다.

    [memos]: {memo_context}
    [purchase history]: {p_context}
    
    summary:
    """
    response = ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': prompt}])
    summary = response['message']['content'].strip()
    
    # DB update
    with engine.begin() as update_conn:
        update_conn.execute(text("""
            UPDATE CUSTOMER SET MEMO = :summary, SUMMARY_TIME = CURRENT_TIMESTAMP WHERE CUSTOMER_ID = :cid
        """), {"summary": summary, "cid": customer_id})
# ------------------------------------------
#  RAG
# ------------------------------------------


