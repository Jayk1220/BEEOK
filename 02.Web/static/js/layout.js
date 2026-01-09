document.addEventListener('DOMContentLoaded', function() {
    const chatWindow = document.getElementById('chatbot-window');
    const chatMessages = document.getElementById('chatbot-messages');
    const chatInput = document.getElementById('chat-input');
    const launcher = document.getElementById('chatbot-launcher');

    window.toggleChatbot = function() {
        const isVisible = chatWindow.style.display === 'flex';
        if (isVisible) {
            chatWindow.style.display = 'none';
            localStorage.setItem('chat_window_state', 'closed');
        } else {
            chatWindow.style.display = 'flex';
            localStorage.setItem('chat_window_state', 'open');
            chatInput.focus();
            scrollToBottom();
        }
    };

    if (launcher) launcher.onclick = window.toggleChatbot;

    function appendMessage(role, text, save = true) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `msg ${role}`;
        msgDiv.innerText = text;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
        if (save) saveChatHistory();
    }

    // 실제 서버 통신 로직으로 수정
    window.sendChatMessage = async function() {
        const text = chatInput.value.trim();
        if (!text) return;
        
        appendMessage('user', text);
        chatInput.value = '';

        // 로딩 표시 (선택 사항)
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'msg bot loading';
        loadingDiv.innerText = "생각 중...";
        chatMessages.appendChild(loadingDiv);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            
            chatMessages.removeChild(loadingDiv); // 로딩 제거
            appendMessage('bot', data.reply || data.error);
        } catch (error) {
            chatMessages.removeChild(loadingDiv);
            appendMessage('bot', "서버 연결에 실패했습니다.");
        }
    };

    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChatMessage();
        });
    }

    function scrollToBottom() { chatMessages.scrollTop = chatMessages.scrollHeight; }
    function saveChatHistory() { localStorage.setItem('beeok_chat_log', chatMessages.innerHTML); }

    function init() {
        const savedLog = localStorage.getItem('beeok_chat_log');
        if (savedLog) chatMessages.innerHTML = savedLog;
        else appendMessage('bot', "무엇을 도와드릴까요?", false);

        if (localStorage.getItem('chat_window_state') === 'open') {
            chatWindow.style.display = 'flex';
            scrollToBottom();
        }
    }
    init();
});