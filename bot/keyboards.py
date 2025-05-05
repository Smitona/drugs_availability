from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

main_menu = InlineKeyboardMarkup(
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
