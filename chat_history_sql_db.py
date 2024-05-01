# chat_history_sql_db.py
from collections import Counter
from datetime import datetime, timezone
import sqlite3
import string


# Database Code
class AIMessageDB:
    def __init__(self, content):
        # Iso format timestamp
        self.timestamp = datetime.now().isoformat()
        self.role = 'ai'
        self.content = content


class HumanMessageDB:
    def __init__(self, content):
        # Iso format timestamp
        self.timestamp = datetime.now().isoformat()
        self.role = 'user'
        self.content = content


class ChatHistoryDB:
    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def initialize(self):
        with self._connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY, 
                    timestamp TEXT,
                    role TEXT,
                    content TEXT
                )
            ''')

    def add_message(self, message):
        with self._connect() as conn:
            conn.execute('INSERT INTO chat_history (timestamp, role, content) VALUES (?, ?, ?)',
                         (message.timestamp, message.role, message.content))

    def get_last_messages(self, n):
        with self._connect() as conn:
            cursor = conn.execute(
                'SELECT * FROM (SELECT * FROM chat_history ORDER BY id DESC LIMIT ?) ORDER BY id ASC',
                (n,))
            return [HumanMessageDB(row[2]) if row[1] == 'user' else AIMessageDB(row[2])
                    for row in cursor.fetchall()]

    def clear_chat_history(self):
        with self._connect() as conn:
            conn.execute('DELETE FROM chat_history')

    def get_all_messages(self):
        with self._connect() as conn:
            cursor = conn.execute(
                'SELECT id, timestamp, role, content FROM chat_history ORDER BY timestamp ASC')
            return cursor.fetchall()

    def retrieve_relevant_messages(self, query, max_results=5):
        """
        Retrieve relevant messages from the chat history based on the query.

        :param query: The search query as a string.
        :param max_results: Maximum number of relevant messages to return.
        :return: A list of relevant messages, each with its score.
        """
        query_words = Counter(
            query.translate(str.maketrans('', '', string.punctuation)).lower().split())

        with self._connect() as conn:
            cursor = conn.execute('SELECT content FROM chat_history')
            all_messages = cursor.fetchall()

            scored_messages = []
            for msg in all_messages:
                msg_words = Counter(
                    msg[0].translate(str.maketrans('', '', string.punctuation)).lower().split())
                common_words = query_words & msg_words
                score = sum(common_words.values())
                scored_messages.append((msg[0], score))

            # Sort messages by score and return top 'max_results' messages
            scored_messages.sort(key=lambda x: x[1], reverse=True)
            return scored_messages[:max_results] if scored_messages else []
