import telebot
from database import DatabaseManager
from typing import Optional

class ReferralBot:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)
        self.db = DatabaseManager()
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.bot.message_handler(commands=["start"])
        def start_command_handler(message):
            args = message.text.split()
            user_id = message.from_user.id
            username = message.from_user.username
            
            # Обработка реферальной ссылки
            referrer_id = None
            if len(args) > 1:
                try:
                    referrer_id = int(args[1])
                except ValueError:
                    pass
            
            # Регистрация пользователя
            self.db.register_user(user_id, username, referrer_id)
            
            welcome_message = (
                "Добро пожаловать!\n\n"
                "🎯 Для получения реферальной ссылки используйте команду /ref\n"
                "📊 Для просмотра статистики используйте команду /stats"
            )
            self.bot.send_message(message.chat.id, welcome_message)
        
        @self.bot.message_handler(commands=["ref"])
        def ref_command_handler(message):
            user_id = message.from_user.id
            ref_link = self.db.get_referral_link(user_id)
            bonus = self.db.get_referral_bonus()
            
            self.bot.send_message(
                message.chat.id,
                f"Ваша реферальная ссылка:\n\n{ref_link}\n\n"
                f"Вы получите {bonus} баллов за каждого приглашенного пользователя!"
            )
        
        @self.bot.message_handler(commands=["stats"])
        def stats_command_handler(message):
            user_id = message.from_user.id
            stats = self.db.get_user_stats(user_id)
            
            stats_message = (
                f"Ваша статистика:\n\n"
                f"Приглашено пользователей: {stats['invited_count']}\n"
                f"Текущий баланс: {stats['balance']} баллов"
            )
            if stats['referrer_id']:
                stats_message += f"\nВаш реферер: {stats['referrer_id']}"
            
            self.bot.send_message(message.chat.id, stats_message)
    
    def run(self):
        self.bot.polling(none_stop=True)
