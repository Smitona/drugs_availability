from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.api.db import is_favorite_drug

main_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='🔍 Поиск препарата', callback_data='search_drug'
            )],
            [InlineKeyboardButton(
                text='Избранные препараты',
                callback_data='favorite_drugs'
            )]
        ]
    )

search_cancel = InlineKeyboardMarkup(
    inline_keyboard=[
            [InlineKeyboardButton(
                text='❌ Отменить поиск', callback_data='cancel_search'
            )]
        ]
)


async def fav_drugs_keyboard(user_id: int) -> InlineKeyboardMarkup:
# заглушка для ручного тестирования
    favorite_drugs = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='{drug_name}', callback_data=f'drug_{drug_id}'
                )],
                [InlineKeyboardButton(
                    text='{drug_name}', callback_data=f'drug_{drug_id}'
                )]
            ]
        )


async def add_fav_drugs_keyboard(
        user_id: int, drug_id: int
) -> InlineKeyboardMarkup:
    is_favorite = await is_favorite_drug(user_id, drug_id)

    if not is_favorite:
        keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text='Добавить в избранное ⭐️ препарат',
                        callback_data=f'add_fav_{drug_id}'
                    )]
                ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text='Удалить из избранного ⭐️ препарат',
                        callback_data=f'remove_fav_{drug_id}'
                    )]
                ]
        )

    return keyboard


async def create_drugs_keyboard(
        drugs: List[dict], page: int = 0, items_per_page: int = 4
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с пагинацией для списка лекарств

    Args:
        drugs: список названий лекарств
        page: текущая страница (начиная с 0)
        items_per_page: количество элементов на странице
    """

    if not drugs:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='🔍 Поиск препарата',
                callback_data='search_drug'
            )]
        ])

    start_index = page * items_per_page
    end_index = start_index + items_per_page
    current_drugs = drugs[start_index:end_index]

    keyboard_buttons = []

    for drug in current_drugs:
        if isinstance(drug, dict):
            drug_name = drug.get('name', 'Неизвестно')
            drug_dosage = drug.get('dosage', '')
            drug_form = drug.get('form', '')
            drug_numero = drug.get('numero', '')
            drug_id = drug.get('id', '')

            if drug_form:
                if len(drug_form) > 30:
                    drug_form = drug_form.split(' ', 1)[0]

            button_text = '{} {} - {} №{}'.format(
                drug_name, drug_dosage, drug_form, drug_numero
            )

            callback_data = f'drug_{drug_id}_{button_text}'
        else:
            drug_name = str(drug)
            button_text = drug_name

        keyboard_buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=callback_data
            )
        ])

    total_pages = (len(drugs) - 1) // items_per_page + 1
    if total_pages > 1:
        navigation_buttons = []

        if page > 0:
            navigation_buttons.append(
                InlineKeyboardButton(
                    text='⬅️ Назад',
                    callback_data=f'drugs_page_{page-1}'
                )
            )

        navigation_buttons.append(
            InlineKeyboardButton(
                text=f'{page + 1}/{total_pages}', 
                callback_data='current_page'
            )
        )

        if end_index < len(drugs):
            navigation_buttons.append(
                InlineKeyboardButton(
                    text='Вперед ➡️',
                    callback_data=f'drugs_page_{page+1}'
                )
            )

        keyboard_buttons.append(navigation_buttons)

    keyboard_buttons.append(
        [
            InlineKeyboardButton(
                text='🔍 Новый поиск', callback_data='search_drug'
            ),
            InlineKeyboardButton(
                text='❌ Закрыть', callback_data='close_search'
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)