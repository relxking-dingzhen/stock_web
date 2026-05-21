function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 添加用户消息到聊天框
    addMessage('user', message);
    input.value = '';
    
    // 发送到后端
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `message=${encodeURIComponent(message)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.code === 200) {
            addMessage('ai', data.data.response);
        } else {
            addMessage('ai', '抱歉，处理您的请求时出现错误。');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage('ai', '抱歉，服务器出现错误。');
    });
}

function addMessage(type, content) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message mb-3`;
    
    messageDiv.innerHTML = `
        <div class="p-3 rounded shadow-sm">
            <strong class="${type === 'user' ? 'text-primary' : 'text-primary'}">
                ${type === 'user' ? '你：' : '小巴：'}
            </strong>
            <p class="mb-0">${content}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    const chatBox = document.getElementById('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 按回车发送消息
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('user-input');
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // 阻止默认的换行行为
            sendMessage();
        }
    });
});