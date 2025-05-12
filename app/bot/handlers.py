import json

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from app.bot.keyboards import main_menu, favorite_drugs
from app.api.db import forms_from_DB
from app.api.api_requests import make_request, write_data


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Приветствует пользователя и показывает основыне кнопки.

    Команда /start
    """
    await message.answer(
        f"""
        Здравствуйте, {hbold(message.from_user.full_name)}!
        """,
        reply_markup=main_menu
    )


@router.callback_query(lambda c: c.data == 'search_drug')
async def callback_search_drug_handler(
    callback_query: types.CallbackQuery
) -> None:
    """
    Сообщение перед запросом в API.

    Команда /search_drug
    """
    await callback_query.message.answer("Введите название препарата для поиска.")
    await callback_query.answer()


@router.callback_query(lambda c: c.data == 'favorite_drugs')
async def callback_favorite_drugs(
    callback_query: types.CallbackQuery
) -> None:
    """
    Выводит на кнопках сохранённые пользом препараты.

    Команда /favorite_drugs
    """

    # callback должен отдавать ответ из БД по препарату

    await callback_query.message.edit_text(
        text="Выберите препарат", reply_markup=favorite_drugs
    )
    await callback_query.answer()


@router.message()
async def handle_user_input(message: Message) -> None:
    """
    Отправляет запрос в API/ищет в БД.
    """

    drug = str(message.text)
    response = await make_request(drug)
    await write_data(response)

    result = await forms_from_DB(drug)

    await message.answer(result)
