from bot import ReferralBot
import os

def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("Не найден TELEGRAM_BOT_TOKEN в переменных окружения")
    
    bot = ReferralBot(token)
    bot.run()

if __name__ == "__main__":
    main()
