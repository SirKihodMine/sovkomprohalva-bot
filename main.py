import asyncio
import nest_asyncio
from bot import main

# Чтобы работать с вложенными event loops
nest_asyncio.apply()

asyncio.run(main())
