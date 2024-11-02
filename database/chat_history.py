import sqlite3
from datetime import datetime

class ChatHistory:
    def __init__(self, db_path="chat_history.db"):
        """Initialize chat history with database path"""
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Conversations table
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     github_url TEXT NOT NULL,
                     created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        
        # Messages table
        c.execute('''CREATE TABLE IF NOT EXISTS messages
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     conversation_id INTEGER NOT NULL,
                     message TEXT NOT NULL,
                     response TEXT NOT NULL,
                     timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                     FOREIGN KEY (conversation_id) REFERENCES conversations (id))''')
        
        conn.commit()
        conn.close()

    def start_conversation(self, github_url):
        """Start a new conversation and return its ID"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("""INSERT INTO conversations (github_url, created_at) 
                        VALUES (?, ?)""", (github_url, datetime.now()))
            conversation_id = c.lastrowid
            conn.commit()
            return conversation_id
        finally:
            conn.close()

    def add_message(self, conversation_id, message, response):
        """Add a message and its response to a conversation"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("""INSERT INTO messages (conversation_id, message, response, timestamp)
                        VALUES (?, ?, ?, ?)""",
                     (conversation_id, message, response, datetime.now()))
            conn.commit()
        finally:
            conn.close()

    def get_conversation_history(self, conversation_id):
        """Get the full history of a conversation"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            # Get conversation details
            c.execute("""SELECT id, github_url, created_at 
                        FROM conversations 
                        WHERE id = ?""", (conversation_id,))
            conversation = c.fetchone()
            
            if not conversation:
                raise ValueError(f"Conversation with ID {conversation_id} not found")
            
            # Get messages
            c.execute("""SELECT message, response, timestamp 
                        FROM messages 
                        WHERE conversation_id = ?
                        ORDER BY timestamp""", (conversation_id,))
            messages = c.fetchall()
            
            return {
                'id': conversation['id'],
                'github_url': conversation['github_url'],
                'created_at': datetime.strptime(conversation['created_at'], '%Y-%m-%d %H:%M:%S.%f'),
                'messages': [
                    {
                        'message': msg['message'],
                        'response': msg['response'],
                        'timestamp': datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                    } for msg in messages
                ]
            }
        finally:
            conn.close()

    def get_all_conversations(self):
        """Get all conversations with their basic info"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            c.execute("""SELECT id, github_url, created_at 
                        FROM conversations 
                        ORDER BY created_at DESC""")
            
            conversations = [
                {
                    'id': row['id'],
                    'github_url': row['github_url'],
                    'created_at': datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S.%f')
                }
                for row in c.fetchall()
            ]
            
            return conversations
        finally:
            conn.close()

    def delete_conversation(self, conversation_id):
        """Delete a conversation and all its messages"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Delete messages first (due to foreign key constraint)
            c.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            
            # Then delete the conversation
            c.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
        finally:
            conn.close()

    def clear_all_history(self):
        """Clear all conversations and messages"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Delete all messages first (due to foreign key constraint)
            c.execute("DELETE FROM messages")
            
            # Then delete all conversations
            c.execute("DELETE FROM conversations")
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
        finally:
            conn.close()

    def get_conversation_stats(self, conversation_id):
        """Get statistics for a conversation"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("""SELECT 
                            COUNT(*) as message_count,
                            MIN(timestamp) as first_message,
                            MAX(timestamp) as last_message
                        FROM messages 
                        WHERE conversation_id = ?""", (conversation_id,))
            
            stats = c.fetchone()
            return {
                'message_count': stats[0],
                'first_message': datetime.strptime(stats[1], '%Y-%m-%d %H:%M:%S.%f') if stats[1] else None,
                'last_message': datetime.strptime(stats[2], '%Y-%m-%d %H:%M:%S.%f') if stats[2] else None
            }
        finally:
            conn.close()