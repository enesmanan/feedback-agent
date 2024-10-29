from datetime import datetime
import sqlite3

class ChatHistory:
    def __init__(self, db_path="chat_history.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Conversations table
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     github_url TEXT,
                     created_at TIMESTAMP)''')
        
        # Messages table
        c.execute('''CREATE TABLE IF NOT EXISTS messages
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     conversation_id INTEGER,
                     message TEXT,
                     response TEXT,
                     timestamp TIMESTAMP,
                     FOREIGN KEY(conversation_id) REFERENCES conversations(id))''')
        
        conn.commit()
        conn.close()

    def start_conversation(self, github_url):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("INSERT INTO conversations (github_url, created_at) VALUES (?, ?)",
                 (github_url, datetime.now()))
        conversation_id = c.lastrowid
        
        conn.commit()
        conn.close()
        
        return conversation_id

    def add_message(self, conversation_id, message, response):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""INSERT INTO messages (conversation_id, message, response, timestamp)
                    VALUES (?, ?, ?, ?)""",
                 (conversation_id, message, response, datetime.now()))
        
        conn.commit()
        conn.close()

    def get_conversation_history(self, conversation_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Conversation details
        c.execute("SELECT github_url FROM conversations WHERE id = ?", (conversation_id,))
        github_url = c.fetchone()[0]
        
        # Messages
        c.execute("""SELECT message, response, timestamp 
                    FROM messages 
                    WHERE conversation_id = ?
                    ORDER BY timestamp""", (conversation_id,))
        messages = c.fetchall()
        
        conn.close()
        
        return {
            'github_url': github_url,
            'messages': [{'message': m[0], 'response': m[1], 'timestamp': m[2]} 
                        for m in messages]
        }