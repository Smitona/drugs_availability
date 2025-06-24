from typing import List
import hashlib
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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


# заглушка для ручного тестирования
favorite_drugs = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Ранвэк', callback_data='ранвэк'
            )],
            [InlineKeyboardButton(
                text='Пентаса', callback_data='пентаса'
            )]
        ]
    )


def create_drugs_keyboard(
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
            drug_id = drug.get('id', '')

            button_text = drug_name
            if drug_dosage:
                button_text += f" {drug_dosage}"
            if drug_form:
                button_text += f" ({drug_form})"

            if len(button_text) > 60:
                button_text = button_text[:57] + "..."

            callback_data = f'drug_{drug_id}'
        else:
            drug_name = str(drug)
            button_text = drug_name

            if len(drug_name) > 40:
                drug_hash = hashlib.md5(drug_name.encode()).hexdigest()[:10]
                callback_data = f'drug_h_{drug_hash}'
            else:
                clean_name = ''.join(c for c in drug_name if c.isalnum() or c in '_-')
                callback_data = f'drug_{clean_name}'[:64]

        if len(callback_data.encode('utf-8')) > 64:
            drug_hash = hashlib.md5(str(drug).encode()).hexdigest()[:10]
            callback_data = f'drug_h_{drug_hash}'

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