import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Проверяем существующие колонки
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]
print("Существующие колонки:", columns)

# Добавляем total_deposit если нет
if 'total_deposit' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN total_deposit REAL DEFAULT 0")
    print("✅ Добавлена колонка total_deposit")

# Добавляем другие возможные отсутствующие колонки
if 'balance' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0")

conn.commit()
conn.close()
print("✅ База данных обновлена!")