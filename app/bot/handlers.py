from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.api.db import forms_from_DB, return_data_from_DB, save_favorite_drug, \
    get_favorite_drugs
from app.api.api_requests import make_request, write_data
from app.bot.keyboards import main_menu, search_cancel, \
    create_drugs_keyboard, add_fav_drugs_keyboard, Pagination
from app.bot.utils import prettify_info


router = Router()


class DrugSearchStates(StatesGroup):
    waiting_for_drug_name = State()
    waiting_for_drug_form = State()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Приветствует пользователя и показывает основыне кнопки.

    Команда /start
    """
    await message.answer(
        text=(
            f'Здравствуйте, {hbold(message.from_user.full_name)}!'
        ),
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


@router.callback_query(F.data.startswith('add_fav_'))
async def handle_add_to_favorite(
    callback_query: types.CallbackQuery,
) -> None:
    """
    Сохраняет в БД препарат и форму за пользователем.
    """
    try:
        drug_id = int(callback_query.data.split('_')[2])

        user_id = callback_query.from_user.id

        result = await save_favorite_drug(user_id, drug_id)

        if result:
            await callback_query.answer("Препарат добавлен в избранное ✅")
    except Exception as e:
        await callback_query.answer("Произошла ошибка, попробуйте позже ❌")
        print(f"Ошибка при добавлении в избранное: {e}")


@router.callback_query(F.data == 'cancel_search')
async def cancel_drug_search(
    callback_query: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Отмена поиска
    """
    await state.clear()
    await callback_query.message.edit_text(
        '🔍 Поиск отменен',
        reply_markup=main_menu
    )
    await callback_query.answer()


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
        # response = await make_request(drug_name)
        # await write_data(response)
        found_drugs = await forms_from_DB(drug_name)

        await state.update_data(
            search_results=found_drugs,
            search_query=drug_name,
            current_page=0
        )
        await loading_message.delete()

        if found_drugs:
            await message.answer(
                text='Найденные формы:',
                reply_markup=await create_drugs_keyboard(found_drugs, page=0)
            )
        else:
            await message.answer(
                text=(
                    f'❌ По запросу "{drug_name}" ничего не найдено.\n'
                    'Попробуйте изменить запрос или проверьте правильность написания.'
                ),
                reply_markup=main_menu
            )
            await state.clear()

    except Exception as e:
        await loading_message.delete()
        await message.answer(
            '❌ Произошла ошибка при поиске. Попробуйте еще раз.',
            reply_markup=main_menu
        )
        print(f"Ошибка поиска препаратов: {e}")
        await state.clear()


@router.callback_query(Pagination.filter())
async def handle_drugs_pagination(
    callback: types.CallbackQuery,
    callback_data: Pagination,
    state: FSMContext
) -> None:
    """Обработчик пагинации"""
    data = await state.get_data()
    page = callback_data.page

    drugs_list = []
    message_text = ""

    if 'search_results' in data:
        drugs_list = data.get('search_results', [])
        message_text = "Результаты поиска"
    elif 'favorite_drugs' in data:
        drugs_list = data.get('favorite_drugs', [])
        message_text = "Избранные препараты"

    if drugs_list:
        await state.update_data(current_page=page)
        new_keyboard = await create_drugs_keyboard(drugs_list, page=page)

        try:
            await callback.message.edit_text(
                text=message_text,
                reply_markup=new_keyboard
            )
        except Exception as create_keyboard_error:
            await callback.message.edit_reply_markup(
                reply_markup=new_keyboard
            )
            print(f'Ошибка создания клавиатуры: {create_keyboard_error}')

    await callback.answer()


@router.callback_query(F.data.startswith('drug_'))
async def handle_drug_selection(
    callback_query: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Ответ из БД по наличию формы.
    """
    await state.set_state(DrugSearchStates.waiting_for_drug_form)

    drug_id = int(callback_query.data.split('_')[1])
    drug_name = callback_query.data.split('_')[2]
    user_id = callback_query.from_user.id
    loading_message = await callback_query.message.answer(
            '🔍 Ищу по аптекам...'
        )

    raw_drug_info = await return_data_from_DB(drug_id)
    drug_info = await prettify_info(raw_drug_info)

    await state.update_data(
            search_results=drug_info, search_query=drug_id
        )
    await state.clear()
    await loading_message.delete()

    if drug_info:
        await callback_query.message.answer(
            text=(
                f'Наличие <b>{drug_name}</b>:\n'
                f'{drug_info}'
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=await add_fav_drugs_keyboard(user_id, drug_id)
        )
    else:
        await callback_query.message.answer("Произошла ошибка поиска в базе.")


@router.callback_query(F.data == 'favorite_drugs')
async def handle_favorite_drugs(
    callback_query: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Выводит на кнопках сохранённые пользом препараты.
    """

    try:
        user_id = callback_query.from_user.id
        fav_list = await get_favorite_drugs(user_id)
        await state.update_data(
            search_results=fav_list, search_query=user_id
        )

        if fav_list:
            new_keyboard = await create_drugs_keyboard(fav_list, page=0)
            await callback_query.message.answer(
                text="Избранные препараты",
                reply_markup=new_keyboard
            )
        else:
            await callback_query.message.answer(
                text="❌ Вы не добавили ни один препарат в избранное.",
                reply_markup=main_menu
            )
    except Exception as e:
        await callback_query.message.answer(
            '❌ Произошла ошибка при поиске. Попробуйте еще раз.',
            reply_markup=main_menu
        )
        print(f"Ошибка поиска избранного: {e}")
