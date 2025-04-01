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
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Поиск препарата', callback_data='search_drug'
            )],
            [InlineKeyboardButton(
                text='Избранные препараты',
                callback_data='favorite_drugs'
            )]
        ]
    )

    await message.answer(
        f"""
        Здравствуйте, {hbold(message.from_user.full_name)}!
        """,
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == 'search_drug')
async def callback_search_drug_handler(
    callback_query: types.CallbackQuery
) -> None:
    await callback_query.message.answer("Введите название препарата для поиска.")
    await callback_query.answer()


@router.callback_query(lambda c: c.data == 'favorite_drugs')
async def callback_favorite_drugs(
    callback_query: types.CallbackQuery
) -> None:

    # Добавить select drug.name и drug.dosage для кнопок у польза.
    # callback должен отдавать ответ из кеша/БД по препарату
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Ранвэк', callback_data='ранвэк'
            )],
            [InlineKeyboardButton(
                text='Пентаса', callback_data='пентаса'
            )]
        ]
    )

    await callback_query.message.edit_text(
        text="Выберите препарат", reply_markup=keyboard
    )
    await callback_query.answer()


@router.message()
async def handle_user_input(message: Message) -> None:

    drug = str(message.text)
    result = json.dumps(make_request(drug), ensure_ascii=False, indent=2)

    formatted_result = f"<pre>{result}</pre> Попробуйте повторить поиск позже."

    await message.answer(formatted_result, parse_mode="HTML")


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
