import asyncio
import nest_asyncio
from bot import main

# Разрешаем использование asyncio.run() на Render
nest_asyncio.apply()

# Запуск основной функции
asyncio.run(main())
