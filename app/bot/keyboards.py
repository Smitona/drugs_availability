from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
                    )],
                    [InlineKeyboardButton(
                        text='🔍 Новый поиск', callback_data='search_drug'
                    )],
                    [InlineKeyboardButton(
                        text='Избранные препараты',
                        callback_data='favorite_drugs'
                    )]
                ]
        )
    else:
        keyboard = main_menu

    return keyboard


class Pagination(CallbackData, prefix="page"):
    page: int


async def create_drugs_keyboard(
        drugs: List[dict], page: int = 0, items_per_page: int = 4
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с пагинацией для списка лекарств

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
    builder = InlineKeyboardBuilder()

    start_index = page * items_per_page
    end_index = start_index + items_per_page
    current_drugs = drugs[start_index:end_index]

    keyboard_buttons = []

    for drug in current_drugs:
        drug_name = drug.get('name', 'Неизвестно')
        drug_dosage = drug.get('dosage', '')
        drug_form = drug.get('form', '')
        drug_numero = drug.get('numero', '')
        drug_id = drug.get('id', '')

        if drug_form and len(drug_form) > 30:
            drug_form = drug_form.split(' ', 1)[0]

        button_text = '{} {} - {} №{}'.format(
            drug_name, drug_dosage, drug_form, drug_numero
        )
        callback_data = f'drug_{drug_id}_{drug_name}'

        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        ))

    total_pages = len(drugs) // items_per_page
    if total_pages > 1:
        navigation_buttons = []

        if page > 0:
            navigation_buttons.append(
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data=Pagination(page=page - 1).pack()
                )
            )

        navigation_buttons.append(
            InlineKeyboardButton(
                text=f'{page + 1} / {total_pages}',
                callback_data='current_page'
            )
        )

        if end_index < len(drugs):
            navigation_buttons.append(
                InlineKeyboardButton(
                    text='➡️',
                    callback_data=Pagination(page=page + 1).pack()
                )
            )

        builder.row(*navigation_buttons)

    builder.row(
        InlineKeyboardButton(
            text='🔍 Новый поиск', callback_data='search_drug'
        ),
        InlineKeyboardButton(
            text='❌ Закрыть', callback_data='close_search'
        )
    )

    builder.row(*keyboard_buttons)

    return builder.as_markup()
