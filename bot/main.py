import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()

from handlers import router

logging.basicConfig(level=logging.INFO)


async def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        raise RuntimeError('TELEGRAM_BOT_TOKEN не задан в переменных окружения')

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    logging.info('Запуск SULTAN Telegram-бота...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
