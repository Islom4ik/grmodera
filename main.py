# Активатор всех модулей и всего кода
from data.loader import dp, executor, papp
import handlers
import asyncio

# async def loader_pyrogram():
    # await asyncio.gather(papp.start())
    # print('Pyrogram Client запущен.')

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(loader_pyrogram())
    executor.start_polling(dp, skip_updates=True)