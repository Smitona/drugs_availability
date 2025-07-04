import asyncio
import logging
import sys
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties


from app.api.db import create_tables
from app.api.api_requests import make_request, write_data
from app.bot.handlers import router


load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')

bot = Bot(
        token=BOT_TOKEN,
        session=AiohttpSession(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

dp = Dispatcher()
dp.include_router(router)


async def main() -> None:
    #await create_tables()
    #await write_data(await make_request('равнэк'))
    #await write_data(await make_request('пентаса'))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
