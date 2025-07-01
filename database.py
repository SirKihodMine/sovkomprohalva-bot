import sqlite3

# Функция Создаёт таблицу пользователей, если её ещё нет
def init_db():
    """Создаёт таблицу пользователей, если её ещё нет"""
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            referred_by TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Функция Добавляет пользователя в базу данных
def add_user(user_id: str, username: str, referred_by: str = None):
    """Добавляет пользователя в базу данных"""
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, referred_by)
        VALUES (?, ?, ?)
    ''', (user_id, username, referred_by))
    conn.commit()
    conn.close()

# Функция Возвращает данные пользователя по ID
def get_user(user_id: str):
    """Возвращает данные пользователя по ID"""
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Функция Возвращает количество пользователей, которых пригласил referrer_id
def count_referrals(referrer_id: str):
    """Возвращает количество пользователей, которых пригласил referrer_id"""
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE referred_by = ?', (referrer_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Функция, которая возвращает список рефереров с количеством их рефералов
def get_top_referrers(limit=10):
    """Возвращает список из top N рефереров и количество их рефералов"""
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT referred_by, COUNT(*) as count 
        FROM users 
        WHERE referred_by IS NOT NULL 
        GROUP BY referred_by 
        ORDER BY count DESC 
        LIMIT ?
    ''', (limit,))
    top_referrers = cursor.fetchall()
    conn.close()
    return top_referrers

def get_all_users():
    """Возвращает список всех пользователей из базы данных"""
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    result = [row[0] for row in cursor.fetchall()]
    conn.close()
    return result