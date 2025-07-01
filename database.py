import sqlite3
from typing import Optional, List, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "users.db"):
        self.conn = sqlite3.connect(db_path)
        self.setup_tables()
    
    def setup_tables(self):
        """Создает необходимые таблицы в базе данных"""
        cursor = self.conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                referrer_id INTEGER,
                invited_count INTEGER DEFAULT 0,
                balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица транзакций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                transaction_type TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        self.conn.commit()
    
    def register_user(self, user_id: int, username: Optional[str], referrer_id: Optional[int]) -> bool:
        """Регистрирует нового пользователя"""
        cursor = self.conn.cursor()
        
        # Проверяем существование реферера
        if referrer_id:
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_id=?", (referrer_id,))
            if cursor.fetchone()[0] == 0:
                referrer_id = None
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, referrer_id)
                VALUES (?, ?, ?)
            ''', (user_id, username, referrer_id))
            
            if referrer_id:
                # Обновляем счетчик приглашенных для реферера
                cursor.execute('''
                    UPDATE users 
                    SET invited_count = invited_count + 1,
                        balance = balance + ?
                    WHERE user_id = ?
                ''', (self.get_referral_bonus(), referrer_id))
                
                # Логируем транзакцию
                cursor.execute('''
                    INSERT INTO transactions 
                    (user_id, amount, transaction_type, description)
                    VALUES (?, ?, ?, ?)
                ''', (referrer_id, self.get_referral_bonus(), 'referral_reward', 
                      f'Награда за приглашение пользователя {user_id}'))
            
            self.conn.commit()
            return True
        except sqlite3.Error:
            self.conn.rollback()
            return False
    
    def get_referral_link(self, user_id: int) -> str:
        """Генерирует реферальную ссылку"""
        bot_username = "@testymynebot_bot"
        return f"https://t.me/{bot_username}?start={user_id}"
    
    def get_referral_bonus(self) -> float:
        """Возвращает сумму бонуса за реферала"""
        return 10.0  # Можно изменить в зависимости от настроек
    
    def get_user_stats(self, user_id: int) -> dict:
        """Получает статистику пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT invited_count, balance, referrer_id 
            FROM users 
            WHERE user_id=?
        ''', (user_id,))
        stats = cursor.fetchone()
        
        if not stats:
            return {"invited_count": 0, "balance": 0.0, "referrer_id": None}
        
        return {
            "invited_count": stats[0],
            "balance": stats[1],
            "referrer_id": stats[2]
        }
