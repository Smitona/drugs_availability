from os import getenv
from dotenv import load_dotenv

# import aiohttp
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

load_dotenv()


TG_TOKEN = getenv('TOKEN')
dp = Dispatcher()


@dp.message()
async def command_start_handler(message: Message) -> None:
    """
    Handler for messages '/start' command
    """
    await message.answer(
        f'Здравствуйте, {hbold(message.from_user.full_name)}!'
    )


async def main() -> None:
    bot = Bot(token=TG_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
