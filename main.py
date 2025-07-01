import asyncio
import nest_asyncio
from bot import main

# Разрешаем вложенные event loops
nest_asyncio.apply()

# Запуск бота
asyncio.run(main())
