from flask import Flask, render_template, request, jsonify
from database.chat_history import ChatHistory
from utils.github_handler import GitHubHandler
from utils.notebook_handler import NotebookHandler
from analyzers.code_analyzer import CodeAnalyzer
from formatters.output_formatter import OutputFormatter
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

app = Flask(__name__,
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))

REQUIRED_FOLDERS = [
    'templates',
    'static',
    'static/css',
    'static/js',
    'database'
]

for folder in REQUIRED_FOLDERS:
    if not os.path.exists(folder):
        os.makedirs(folder)

chat_history = ChatHistory()

class CodeFeedbackSystem:
    def __init__(self, openai_api_key):
        self.analyzer = CodeAnalyzer(openai_api_key)
        self.github_handler = GitHubHandler()
        self.notebook_handler = NotebookHandler()
        self.formatter = OutputFormatter()

    def analyze_code(self, github_url):
        try:
            content = self.github_handler.get_file_content(github_url)
            
            if github_url.endswith('.ipynb'):
                content = self.notebook_handler.extract_notebook_code(content)
            elif not github_url.endswith('.py'):
                raise ValueError("Desteklenmeyen dosya formatı")
            
            analysis = self.analyzer.analyze_code(content)
            return self.formatter.format_analysis(analysis)
            
        except Exception as e:
            return f"Hata oluştu: {str(e)}"

    def chat_about_code(self, message, code_context):
        try:
            response = self.analyzer.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Sen bir kod analiz asistanısın. Kullanıcının projesi hakkındaki sorularını yanıtla."},
                    {"role": "user", "content": f"Proje kodu:\n{code_context}\n\nSoru: {message}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Hata oluştu: {str(e)}"

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    github_url = data['url']
    
    # start conversation
    conversation_id = chat_history.start_conversation(github_url)
    
    # analyze code
    feedback_system = CodeFeedbackSystem(app.config['OPENAI_API_KEY'])
    response = feedback_system.analyze_code(github_url)
    
    # save message
    chat_history.add_message(conversation_id, "Kodu analiz et", response)
    
    return jsonify({
        'conversation_id': conversation_id,
        'response': response
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']
    conversation_id = data['conversation_id']
    
    # get code context
    history = chat_history.get_conversation_history(conversation_id)
    github_url = history['github_url']
    
    # chat about code
    feedback_system = CodeFeedbackSystem(app.config['OPENAI_API_KEY'])
    code_context = feedback_system.github_handler.get_file_content(github_url)
    
    if github_url.endswith('.ipynb'):
        code_context = feedback_system.notebook_handler.extract_notebook_code(code_context)
    
    # get response
    response = feedback_system.chat_about_code(message, code_context)
    
    # save message
    chat_history.add_message(conversation_id, message, response)
    
    return jsonify({'response': response})

@app.route('/history/<int:conversation_id>')
def get_history(conversation_id):
    history = chat_history.get_conversation_history(conversation_id)
    return render_template('chat.html', history=history, conversation_id=conversation_id)

if __name__ == '__main__':
    app.config['OPENAI_API_KEY'] = os.environ['OPENAI_API_KEY']
    app.run(debug=True)