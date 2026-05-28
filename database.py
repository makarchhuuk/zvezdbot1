import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._set_admin_balance()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'ru',
                balance REAL DEFAULT 0,
                total_bought INTEGER DEFAULT 0,
                total_sold INTEGER DEFAULT 0,
                total_deposit REAL DEFAULT 0
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount INTEGER,
                recipient TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        self.conn.commit()

    def _set_admin_balance(self):
        from config import ADMIN_ID
        self.cursor.execute("UPDATE users SET balance = 1000 WHERE user_id = ?", (ADMIN_ID,))
        self.conn.commit()

    def add_user(self, user_id):
        self.cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            self.conn.commit()
            return True
        return False

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()

    def update_language(self, user_id, lang):
        self.cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
        self.conn.commit()

    def get_balance(self, user_id):
        self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return row[0] if row else 0.0

    def update_balance(self, user_id, amount):
        self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        self.conn.commit()
        if amount > 0:
            self.cursor.execute("UPDATE users SET total_deposit = total_deposit + ? WHERE user_id = ?", (amount, user_id))
            self.conn.commit()

    def update_user_stats(self, user_id, stars, action):
        if action == "buy":
            self.cursor.execute("UPDATE users SET total_bought = total_bought + ? WHERE user_id = ?", (stars, user_id))
        else:
            self.cursor.execute("UPDATE users SET total_sold = total_sold + ? WHERE user_id = ?", (stars, user_id))
        self.conn.commit()

    def add_order(self, user_id, order_type, amount, recipient):
        self.cursor.execute("INSERT INTO orders (user_id, type, amount, recipient) VALUES (?, ?, ?, ?)",
                            (user_id, order_type, amount, recipient))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_orders(self, user_id, limit=10):
        self.cursor.execute("SELECT id, type, amount, recipient, status FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
        return self.cursor.fetchall()

db = Database()