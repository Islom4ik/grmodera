# Настройка бота - лоадер || токен, секретные ключи, тонкие настройки:
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import dotenv_values
from pyrogram import Client, enums
from pyrogram.enums import ParseMode
config = dotenv_values(".env")
import logging

logging.basicConfig(filename='your_log_file.log', level=logging.INFO)
papp = Client("my_account", api_id=29798988, api_hash="132ba9432841cf06b90616959d697847", parse_mode=ParseMode.HTML)

bot = Bot(config["BOT_TOKEN"], parse_mode='HTML', disable_web_page_preview=True) # BOT_TOKEN можно || нужно указать в .env

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)