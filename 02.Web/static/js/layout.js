document.addEventListener('DOMContentLoaded', function() {
    // --- [1. 필요한 화면 요소들 변수에 담기] ---
    const chatWindow = document.getElementById('chatbot-window');   // 챗봇 전체 창
    const chatMessages = document.getElementById('chatbot-messages'); // 메시지 표시 구역
    const chatInput = document.getElementById('chat-input');       // 글자 입력창
    const launcher = document.getElementById('chatbot-launcher');   // 우측 하단 아이콘

    // --- [2. 챗봇 창 열고 닫기 함수] ---
    window.toggleChatbot = function() {
        const isVisible = chatWindow.style.display === 'flex';
        
        if (isVisible) {
            // [리셋 핵심] 창을 닫을 때 실행
            chatWindow.style.display = 'none';
            
            // 1. 화면의 대화 내용을 즉시 삭제
            chatMessages.innerHTML = ''; 
            // 2. 브라우저 저장소에 기록된 대화 로그 삭제
            localStorage.removeItem('beeok_chat_log');
            // 3. 다시 열었을 때를 대비해 기본 인사말만 새로 추가 (저장은 안 함)
            appendMessage('bot', "무엇을 도와드릴까요? 🐝", false); 
            
            localStorage.setItem('chat_window_state', 'closed');
        } else {
            // 창을 열 때 실행
            chatWindow.style.display = 'flex';
            localStorage.setItem('chat_window_state', 'open');
            
            // 열 때는 기존 기록을 불러오지 않고, 현재 화면 상태(인사말만 있는 상태) 유지
            chatInput.focus();
            scrollToBottom();
        }
    };

    if (launcher) launcher.onclick = window.toggleChatbot;

    // --- [3. 메시지를 화면에 추가하는 함수] ---
    function appendMessage(role, text, save = true) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `msg ${role}`;
        msgDiv.innerText = text;
        chatMessages.appendChild(msgDiv);
        
        scrollToBottom();
        
        // save가 true일 때만 저장 (대화 도중 새로고침 시 유지용)
        if (save) saveChatHistory();
    }

    // --- [4. 서버와 통신 (메시지 전송)] ---
    window.sendChatMessage = async function() {
        const text = chatInput.value.trim();
        if (!text) return;
        
        appendMessage('user', text);
        chatInput.value = '';

        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'msg bot loading';
        loadingDiv.innerText = "생각 중...";
        chatMessages.appendChild(loadingDiv);
        scrollToBottom();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            
            if (chatMessages.contains(loadingDiv)) chatMessages.removeChild(loadingDiv);
            appendMessage('bot', data.reply || data.error);
        } catch (error) {
            if (chatMessages.contains(loadingDiv)) chatMessages.removeChild(loadingDiv);
            appendMessage('bot', "서버 연결에 실패했습니다.");
        }
    };

    // --- [5. 편의 기능 및 보조 함수] ---
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChatMessage();
        });
    }

    function scrollToBottom() { 
        chatMessages.scrollTop = chatMessages.scrollHeight; 
    }

    function saveChatHistory() { 
        localStorage.setItem('beeok_chat_log', chatMessages.innerHTML); 
    }

    // --- [6. 초기화 로직 (페이지 로드 시)] ---
    function init() {
        const savedLog = localStorage.getItem('beeok_chat_log');
        
        // 새로고침 시에도 창이 열려있었다면 대화 내용을 유지, 아니면 리셋
        if (savedLog) {
            chatMessages.innerHTML = savedLog;
        } else {
            chatMessages.innerHTML = '';
            appendMessage('bot', "무엇을 도와드릴까요? 🐝", false);
        }

        if (localStorage.getItem('chat_window_state') === 'open') {
            chatWindow.style.display = 'flex';
            scrollToBottom();
        }
    }

    init();
});