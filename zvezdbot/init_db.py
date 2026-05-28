import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Создаём таблицу users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    balance REAL DEFAULT 0,
    total_deposit REAL DEFAULT 0,
    total_withdraw REAL DEFAULT 0,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Создаём другие нужные таблицы (если есть)
cursor.execute('''
CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("✅ База данных и таблицы созданы!")