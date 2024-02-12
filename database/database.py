# Подключение базы данных MongoDB:
import motor.motor_asyncio
import asyncio
from data.loader import config
from bson.objectid import ObjectId

client = motor.motor_asyncio.AsyncIOMotorClient(config["DB"])
collection = client.bot.botadmin
