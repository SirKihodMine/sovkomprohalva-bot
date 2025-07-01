import sqlite3


def init_db():
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


def add_user(user_id: str, username: str, referred_by: str = None):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, referred_by)
        VALUES (?, ?, ?)
    ''', (user_id, username, referred_by))
    conn.commit()
    conn.close()


def get_user(user_id: str):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def count_referrals(referrer_id: str):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM users 
        WHERE referred_by = ?
    ''', (referrer_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_top_referrers(limit=10):
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
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    result = [row[0] for row in cursor.fetchall()]
    conn.close()
    return result
