import asyncio
import nest_asyncio
from bot import main

# === Чтобы избежать ошибки с event loop ===
nest_asyncio.apply()

asyncio.run(main())
