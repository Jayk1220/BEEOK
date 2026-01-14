document.addEventListener('DOMContentLoaded', function() {
    // --- [1. 변수 선언] ---
    const chatWindow = document.getElementById('chatbot-window');
    const chatMessages = document.getElementById('chatbot-messages');
    const chatInput = document.getElementById('chat-input');
    const launcher = document.getElementById('chatbot-launcher');
    const alerts = document.querySelectorAll('.auto-dismiss');

    // --- [2. 챗봇 기능] ---
    window.toggleChatbot = function() {
        const isVisible = chatWindow.style.display === 'flex';
        if (isVisible) {
            chatWindow.style.display = 'none';
            chatMessages.innerHTML = ''; 
            localStorage.removeItem('beeok_chat_log');
            appendMessage('bot', "무엇을 도와드릴까요? 🐝", false); 
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
        if (!chatMessages) return;
        const msgDiv = document.createElement('div');
        msgDiv.className = `msg ${role}`;
        msgDiv.innerText = text;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
        if (save) saveChatHistory();
    }

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

    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChatMessage();
        });
    }

    function scrollToBottom() { 
        if(chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight; 
    }

    function saveChatHistory() { 
        if(chatMessages) localStorage.setItem('beeok_chat_log', chatMessages.innerHTML); 
    }

    // --- [3. 플래시 메시지 자동 삭제 기능] ---
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // 위치와 투명도 애니메이션
            alert.style.opacity = "0";
            alert.style.transform = "translateX(20px)";
            
            // 애니메이션 완료 후 물리적 공간 제거
            setTimeout(function() {
                alert.style.height = "0";
                alert.style.margin = "0";
                alert.style.padding = "0";
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 500);
        }, 3000); 
    });

    // --- [4. 초기화] ---
    function init() {
        const savedLog = localStorage.getItem('beeok_chat_log');
        if (chatMessages) {
            if (savedLog) {
                chatMessages.innerHTML = savedLog;
            } else {
                appendMessage('bot', "무엇을 도와드릴까요? 🐝", false);
            }
        }
        if (localStorage.getItem('chat_window_state') === 'open' && chatWindow) {
            chatWindow.style.display = 'flex';
            scrollToBottom();
        }
    }
    init();
});