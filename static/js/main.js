document.addEventListener('DOMContentLoaded', function() {
    const md = window.markdownit();
    const messagesDiv = document.getElementById('messages');
    let conversationId = null;

    // Markdown içeriğini render et
    document.querySelectorAll('.markdown-content').forEach(element => {
        element.innerHTML = md.render(element.textContent);
    });

    // GitHub URL form submit
    document.getElementById('urlForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const url = document.getElementById('githubUrl').value;
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });
            
            const data = await response.json();
            conversationId = data.conversation_id;
            
            // URL input'u gizle
            document.getElementById('urlInput').style.display = 'none';
            
            // Chat input'u aktif et
            document.getElementById('userMessage').disabled = false;
            document.getElementById('chatForm').querySelector('button').disabled = false;
            
            // Analiz sonucunu göster
            addMessage('assistant', data.response);
            
        } catch (error) {
            console.error('Error:', error);
            alert('Bir hata oluştu!');
        }
    });

    // Chat form submit
    document.getElementById('chatForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const messageInput = document.getElementById('userMessage');
        const message = messageInput.value;
        
        if (!message.trim()) return;
        
        // Kullanıcı mesajını göster
        addMessage('user', message);
        messageInput.value = '';
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: conversationId
                })
            });
            
            const data = await response.json();
            
            // Assistant yanıtını göster
            addMessage('assistant', data.response);
            
        } catch (error) {
            console.error('Error:', error);
            alert('Bir hata oluştu!');
        }
    });

    function addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender} mb-4`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = sender === 'user' ? 'bg-blue-100 p-3 rounded-lg' : 'bg-gray-100 p-3 rounded-lg markdown-content';
        
        if (sender === 'assistant') {
            contentDiv.innerHTML = md.render(content);
        } else {
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(contentDiv);
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
});