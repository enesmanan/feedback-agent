# Code Feedback Agent

![Python Version](https://img.shields.io/badge/python-3.10.6-blue.svg) ![Flask Version](https://img.shields.io/badge/flask-3.0.3-green.svg) ![OpenAI](https://img.shields.io/badge/OpenAI-GPT4-orange.svg) ![Gemini](https://img.shields.io/badge/Gemini-pro-purple.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg) 


Code Feedback Agent is an interactive web application that analyzes your Python projects on GitHub and provides AI-powered feedback. You can receive detailed analysis of your project and chat with the bot to improve your code.

## 🚀 Features

- 📊 Comprehensive code analysis
- 💬 Interactive chat interface
- 📝 Markdown formatted outputs
- 🔄 Chat history tracking
- 🐍 Python and Jupyter Notebook support
- 🔒 Secure and scalable architecture

## 🛠️ Technologies

- **Backend**: Flask
- **AI**: OpenAI GPT-4 & Gemini Pro
- **Database**: SQLite
- **Frontend**: HTML, CSS (Tailwind), JavaScript

## 📋 Prerequisites

- Python 3.10+
- OpenAI & Gemini API key
- Git & pip

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/enesmanan/feedback-agent.git
cd feedback-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Set `.env` file:
```env
OPENAI_API_KEY="api-key-here"
GEMINI_API_KEY="api-key-here"
DEFAULT_AI_SERVICE=auto
```

5. Run the application:
```bash
python3 app.py # Linux
python app.py  # Windows
```

## 💡 Usage

1. Go to `http://localhost:5000` in your browser
2. Enter your GitHub project URL
3. Review the analysis results
4. Chat with the bot to improve your project

## 📁 Project Structure

```
feedback_agent/
├── templates/              # HTML templates
│   ├── base.html
│   └── chat.html
├── static/                 # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── database/              # Database operations
│   └── chat_history.py
├── utils/                 # Utility functions
│   ├── github_handler.py
│   └── notebook_handler.py
├── analyzers/             # Code analysis
│   └── code_analyzer.py
├── formatters/            # Output formatting
│   └── output_formatter.py
├── config/               # Configuration
│   └── settings.py
├── app.py                # Main application
├── requirements.txt      # Dependencies
└── README.md            # Documentation
```


## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](https://mit-license.org/) file for details.

## 👥 Contact

Enes Fehmi Manan - [@enesfehmimanan](https://www.linkedin.com/in/enesfehmimanan/)


