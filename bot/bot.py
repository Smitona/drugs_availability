from os import getenv
from dotenv import load_dotenv

# import aiohttp
import asyncio
import logging
import sys
import json

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties

from parser.main import make_request

load_dotenv()


TG_TOKEN = getenv('TOKEN')
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Handler for messages '/start' command
    """

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Поиск препарата', callback_data='search_drug'
            )]
        ]
    )

    await message.answer(
        f"""
        Здравствуйте, {hbold(message.from_user.full_name)}!
        """,
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == "search_drug")
async def callback_search_drug_handler(
    callback_query: types.CallbackQuery
) -> None:
    await callback_query.message.answer("Введите название препарата для поиска.")
    await callback_query.answer()


@router.message()
async def handle_user_input(message: Message) -> None:

    drug = str(message.text)
    result = json.dumps(make_request(drug), ensure_ascii=False, indent=2)

    await message.answer(result)


async def main() -> None:
    bot = Bot(
        token=TG_TOKEN,
        session=AiohttpSession(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
