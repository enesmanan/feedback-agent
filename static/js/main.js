document.addEventListener('DOMContentLoaded', function() {
    const md = window.markdownit({
        highlight: function (str, lang) {
            if (lang && Prism.languages[lang]) {
                try {
                    return '<pre class="language-' + lang + '"><code>' +
                           Prism.highlight(str, Prism.languages[lang], lang) +
                           '</code></pre>';
                } catch (__) {}
            }
            return '<pre class="language-none"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
        }
    });

    const messagesDiv = document.getElementById('messages');
    let conversationId = null;

    // Markdown içeriğini render et ve Prism.js'i başlat
    function renderMarkdownAndInitPrism(element) {
        element.innerHTML = md.render(element.textContent);
        Prism.highlightAllUnder(element);
    }

    // Mevcut markdown içeriğini işle
    document.querySelectorAll('.markdown-content').forEach(renderMarkdownAndInitPrism);

    function addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender} mb-4`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = sender === 'user' ? 'bg-blue-100 p-3 rounded-lg' : 'bg-gray-100 p-3 rounded-lg markdown-content';
        
        if (sender === 'assistant') {
            contentDiv.textContent = content;
            renderMarkdownAndInitPrism(contentDiv);
        } else {
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(contentDiv);
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

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
            addMessage('assistant', data.response);
            
        } catch (error) {
            console.error('Error:', error);
            alert('Bir hata oluştu!');
        }
    });
});