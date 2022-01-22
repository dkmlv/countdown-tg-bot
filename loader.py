import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler
from supabase.client import create_client, Client

from data import config

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

sched = Scheduler(
    timezone="Asia/Tashkent",
    daemon=True,
)
sched.start()

logging.basicConfig(
    level=logging.INFO,
    format=u"%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
