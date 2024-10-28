from utils.github_handler import GitHubHandler
from utils.notebook_handler import NotebookHandler
from analyzers.code_analyzer import CodeAnalyzer
from formatters.output_formatter import OutputFormatter

class CodeFeedbackSystem:
    def __init__(self, openai_api_key):
        self.analyzer = CodeAnalyzer(openai_api_key)
        self.github_handler = GitHubHandler()
        self.notebook_handler = NotebookHandler()
        self.formatter = OutputFormatter()

    def provide_feedback(self, github_url):
        """GitHub URL'si için geri bildirim sağlar"""
        try:
            # Retrieve content from GitHub
            content = self.github_handler.get_file_content(github_url)
            
            # notebooksa kodu al
            if github_url.endswith('.ipynb'):
                content = self.notebook_handler.extract_notebook_code(content)
            elif not github_url.endswith('.py'):
                raise ValueError("Desteklenmeyen dosya formatı. Sadece .py ve .ipynb dosyaları desteklenir.")
            
            # Kodu analiz et
            analysis = self.analyzer.analyze_code(content)
            
            # Sonuçları formatla
            feedback = self.formatter.format_analysis(analysis)
            
            return feedback
            
        except Exception as e:
            return f"Hata oluştu: {str(e)}"

if __name__ == "__main__":
    openai_api_key = "OPENAI_API_KEY"
    feedback_system = CodeFeedbackSystem(openai_api_key)
    
    github_url = "https://github.com/emirryilmazz/Fish-Classification/blob/main/main.ipynb"
    feedback = feedback_system.provide_feedback(github_url)
    print(feedback)