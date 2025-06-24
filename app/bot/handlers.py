import json

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.api.db import forms_from_DB
from app.api.api_requests import make_request, write_data
from app.bot.keyboards import main_menu, favorite_drugs, search_cancel, \
    create_drugs_keyboard


router = Router()


class DrugSearchStates(StatesGroup):
    waiting_for_drug_name = State()


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


@router.callback_query(F.data == 'search_drug')
async def callback_search_drug_handler(
    callback_query: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Команда поиска - /search_drug
    """
    await state.set_state(DrugSearchStates.waiting_for_drug_name)
    await callback_query.message.answer(
        '🔍 Введите название препарата или его часть для поиска:',
        reply_markup=search_cancel
    )
    await callback_query.answer()


@router.callback_query(F.data == 'cancel_search')
async def cancel_drug_search(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Отмена поиска
    """
    await state.clear()
    await callback.message.edit_text(
        '🔍 Поиск отменен',
        reply_markup=main_menu
    )
    await callback.answer()


@router.callback_query(F.data == 'close_search')
async def close_search_results(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Завершение поиска
    """
    await state.clear()
    await callback.message.edit_text('✅ Поиск завершен')
    await callback.answer()


@router.message(DrugSearchStates.waiting_for_drug_name)
async def process_drug_search(
    message: Message, state: FSMContext
):
    """
    Обработка названия препарата
    """
    drug_name = message.text.strip()

    loading_message = await message.answer('🔍 Ищу препараты...')

    try:
        response = await make_request(drug_name)
        await write_data(response)
        found_drugs = await forms_from_DB(drug_name)

        await state.update_data(
            search_results=found_drugs, search_query=drug_name
        )
        await state.clear()
        await loading_message.delete()

        if found_drugs:
            await message.answer(
                text='Найденные формы:',
                reply_markup=create_drugs_keyboard(found_drugs, page=0)
            )
        else:
            await message.answer(
                f'❌ По запросу "{drug_name}" ничего не найдено.\n'
                'Попробуйте изменить запрос или проверьте правильность написания.',
                reply_markup=main_menu
            )

    except Exception as e:
        await loading_message.delete()
        await message.answer(
            "❌ Произошла ошибка при поиске. Попробуйте еще раз.",
            reply_markup=main_menu
        )
        print(f"Ошибка поиска препаратов: {e}")


@router.callback_query(F.data.startswith('drugs_page_'))
async def handle_drugs_pagination(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Результаты поиска из БД.
    """
    page = int(callback.data.split('_')[-1])

    data = await state.get_data()
    drugs_list = data.get('search_results', [])

    if drugs_list:
        new_keyboard = create_drugs_keyboard(drugs_list, page=page)
        await callback.message.edit_reply_markup(reply_markup=new_keyboard)

    await callback.answer()


@router.callback_query(F.data.startswith('drug_'))
async def handle_drug_selection(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Выбор препарата.
    """
    drug_name = callback.data.replace('drug_', '')

    await state.clear()

    await callback.message.answer(f'✅ {drug_name.title()}')
    await callback.answer()


@router.callback_query(F.data == 'current_page')
async def handle_current_page(
    callback: types.CallbackQuery
) -> None:
    await callback.answer('Текущая страница')


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
