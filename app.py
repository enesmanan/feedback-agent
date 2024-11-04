from flask import Flask, render_template, request, jsonify
from database.chat_history import ChatHistory
from utils.github_handler import GitHubHandler
from utils.notebook_handler import NotebookHandler
from analyzers.code_analyzer import CodeAnalyzer
from formatters.output_formatter import OutputFormatter
import os
from dotenv import load_dotenv

load_dotenv()

class CodeFeedbackSystem:
    def __init__(self, api_keys):
        self.analyzer = CodeAnalyzer(api_keys)
        self.github_handler = GitHubHandler()
        self.notebook_handler = NotebookHandler()
        self.formatter = OutputFormatter()

    def analyze_code(self, github_url):
        """Analyze code from GitHub URL"""
        try:
            # Get content from GitHub
            content = self.github_handler.get_file_content(github_url)
            
            # Handle Jupyter notebooks
            if github_url.endswith('.ipynb'):
                notebook_data = self.notebook_handler.extract_notebook_code(content)
                analysis = self.analyzer.analyze_code(
                    code=notebook_data['code'], 
                    notebook_data=notebook_data
                )
            elif github_url.endswith('.py'):
                analysis = self.analyzer.analyze_code(code=content)
            else:
                raise ValueError("Unsupported file format. Only .py and .ipynb files are supported.")
            
            return self.formatter.format_analysis(analysis)
            
        except Exception as e:
            return f"Error occurred: {str(e)}"

    def chat_about_code(self, message, code_context):
        """Chat about code using AI"""
        try:
            return self.analyzer.chat_about_code(message, code_context)
        except Exception as e:
            return f"Chat error: {str(e)}"

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_mapping(
        OPENAI_API_KEY=os.getenv('OPENAI_API_KEY'),
        GEMINI_API_KEY=os.getenv('GEMINI_API_KEY'),
        DEFAULT_AI_SERVICE=os.getenv('DEFAULT_AI_SERVICE', 'auto'),
        DATABASE=os.path.join(app.instance_path, 'chat_history.sqlite'),
    )
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize services
    chat_history = ChatHistory(app.config['DATABASE'])
    api_keys = {
        "OPENAI_API_KEY": app.config['OPENAI_API_KEY'],
        "GEMINI_API_KEY": app.config['GEMINI_API_KEY']
    }
    feedback_system = CodeFeedbackSystem(api_keys)

    @app.route('/')
    def home():
        """Home page route with conversation history"""
        histories = chat_history.get_all_conversations()
        return render_template('chat.html', histories=histories)

    @app.route('/analyze', methods=['POST'])
    def analyze():
        """Analyze code from GitHub URL"""
        try:
            data = request.json
            github_url = data['url']
            
            # Start new conversation
            conversation_id = chat_history.start_conversation(github_url)
            
            # Analyze code
            response = feedback_system.analyze_code(github_url)
            
            # Save initial analysis
            chat_history.add_message(conversation_id, "Analyze code", response)
            
            return jsonify({
                'conversation_id': conversation_id,
                'response': response
            })
            
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 400

    @app.route('/chat', methods=['POST'])
    def chat():
        """Handle chat messages"""
        try:
            data = request.json
            message = data['message']
            conversation_id = data['conversation_id']
            
            # Get conversation history
            history = chat_history.get_conversation_history(conversation_id)
            github_url = history['github_url']
            
            # Get code context
            code_context = feedback_system.github_handler.get_file_content(github_url)
            
            if github_url.endswith('.ipynb'):
                code_context = feedback_system.notebook_handler.extract_notebook_code(code_context)
            
            # Get AI response
            response = feedback_system.chat_about_code(message, code_context)
            
            # Save message and response
            chat_history.add_message(conversation_id, message, response)
            
            return jsonify({'response': response})
            
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 400

    @app.route('/history/<int:conversation_id>')
    def get_history(conversation_id):
        """Get chat history for a conversation"""
        try:
            history = chat_history.get_conversation_history(conversation_id)
            histories = chat_history.get_all_conversations()
            return render_template('chat.html', 
                                 history=history, 
                                 histories=histories,
                                 conversation_id=conversation_id)
        except Exception as e:
            return str(e), 400

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        histories = chat_history.get_all_conversations()
        return render_template('chat.html', 
                             error="Page not found",
                             histories=histories), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        histories = chat_history.get_all_conversations()
        return render_template('chat.html', 
                             error="Internal server error",
                             histories=histories), 500

    return app

def init_db():
    """Initialize the database"""
    with app.app_context():
        db_path = app.config['DATABASE']
        chat_history = ChatHistory(db_path)
        chat_history.init_db()

app = create_app()

if __name__ == '__main__':
    # Configuration for running the app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    # Initialize database
    init_db()
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )