import asyncio
import nest_asyncio
from bot import main

# Разрешаем использовать asyncio.run() + run_webhook()
nest_asyncio.apply()

asyncio.run(main())
