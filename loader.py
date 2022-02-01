import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler
from supabase.client import Client, create_client

from data import config

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

storage = RedisStorage2(
    config.REDIS_HOST,
    config.REDIS_PORT,
    config.REDIS_DB,
    config.REDIS_PASSWORD,
)
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
