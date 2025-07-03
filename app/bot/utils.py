from typing import List

SPB_METRO = {
    "Красная": [
        "Девяткино", "Гражданский проспект", "Академическая",
        "Политехническая", "Площадь Мужества", "Лесная", "Выборгская",
        "Площадь Ленина", "Чернышевская", "Площадь Восстания", "Владимирская",
        "Пушкинская", "Технологический институт", "Балтийская", "Нарвская",
        "Кировский завод", "Автово", "Ленинский проспект", "Проспект Ветеранов"
    ],

    "Синяя": [
        "Парнас", "Проспект Просвещения", "Озерки", "Удельная", "Пионерская",
        "Чёрная речка", "Петроградская", "Горьковская", "Невский проспект",
        "Сенная площадь", "Технологический институт", "Фрунзенская",
        "Московские ворота", "Электросила", "Парк Победы", "Московская",
        "Звёздная", "Купчино"
    ],

    "Зелёная": [
        "Приморская", "Василеостровская", "Гостиный двор", "Маяковская",
        "Площадь Александра Невского", "Елизаровская", "Ломоносовская",
        "Пролетарская", "Обухово", "Рыбацкое"
    ],

    "Оранжевая": [
        "Спасская", "Достоевская", "Лиговский проспект",
        "Площадь Александра Невского", "Новочеркасская",
        "Ладожская", "Проспект Большевиков", "Улица Дыбенко"
    ],

    "Фиолетовая": [
        "Комендантский проспект", "Старая Деревня", "Крестовский остров",
        "Чкаловская", "Спортивная", "Адмиралтейская", "Садовая",
        "Звенигородская", "Обводный канал", "Волковская", "Бухарестская",
        "Международная", "Проспект Славы", "Дунайская", "Шушары"
    ]
}

EMODJI = {
    "Красная": "🔴",
    "Синяя": "🔵",
    "Зелёная": "🟢",
    "Оранжевая": "🟠",
    "Фиолетовая": "🟣"
}

BENEFIT_NAMES = {
        'regional': 'Региональная льгота',
        'federal': 'Федеральная льгота',
        'ssz': 'Сердечно-сосудистые заболевания',
        'psychiatry': 'Психиатрическая льгота',
        'refugee': 'Льгота для беженцев',
        'diabetic_kids_2_4': 'Дети с диабетом 2-4 года',
        'diabetic_kids_4_17': 'Дети с диабетом 4-17 лет',
        'hepatitis': 'Гепатит'
    }


async def get_station_emoji(station_name: str) -> str:
    """
    Возвращает эмодзи цвета ветки по названию станции.
    """
    for line_color, stations in SPB_METRO.items():
        if station_name in stations:
            return EMODJI.get(line_color, '⚪️')

    return '🚃'


async def format_update_time(last_update) -> str:
    """Форматирует время обновления для отображения"""
    months = (
        '', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    )

    return '{} {} {} {:02d}:{:02d}'.format(
        last_update.day, months[last_update.month],
        last_update.year, last_update.hour, last_update.minute
    )


async def get_maps_url(address: str) -> str:
    main_url = 'https://maps.yandex.ru/maps/?text='
    return main_url + address


async def format_benefits(pharmacy: dict) -> str:
    """Форматирует строку с льготами"""
    benefits = [
        f'{BENEFIT_NAMES[key]} - <b>{count} шт.</b>'
        for key, count in pharmacy.items()
        if key in BENEFIT_NAMES and count > 0
    ]
    return '\n'.join(benefits)


async def prepare_pharmacy_data(data: List[dict]) -> List[dict]:
    """
    Подготавливает и форматирует данные аптек.
    Возвращает список словарей с отформатированными данными.
    """
    formatted_data = []
    for d in data:
        formatted_data.append({
            'name': d['pharm_name'],
            'maps_url': await get_maps_url(d['pharm_loc']),
            'location': d['pharm_loc'],
            'district': d['pharm_district'],
            'subway': f"{await get_station_emoji(d['pharm_subway'])} {d['pharm_subway']}",
            'phone': '+7812' + d['pharm_phone'],
            'time': await format_update_time(d['last_update']),
            'schedule': '\n'.join(
                f'• {day}: {time}'
                for day, time in d['pharm_work'].items()
                if time != '0:00-0:00'
            ),
            'benefits': await format_benefits(d),
            'separator': "┅" * 20
        })
    return formatted_data


async def build_pharmacy_message(pharmacy_data: dict) -> str:
    """
    Собирает сообщение из подготовленных данных.
    Принимает словарь с отформатированными данными одной аптеки.
    """
    return (
        f'\n<b>{pharmacy_data["name"]}</b>, '
        f'<a href="{pharmacy_data["maps_url"]}">'
        f'📍{pharmacy_data["location"]}</a>\n'
        f'{pharmacy_data["district"]} район, '
        f'{pharmacy_data["subway"]}\n'
        f'☎️ {pharmacy_data["phone"]}\n'
        f'<i>Данные от {pharmacy_data["time"]}</i>\n'
        f'<blockquote expandable>'
        f'{pharmacy_data["benefits"]}\n'
        f'\n Расписание работы льготного отдела:\n'
        f'{pharmacy_data["schedule"]}'
        f'</blockquote>\n'
        f'{pharmacy_data["separator"]}'
    )


async def prettify_info(data: List[dict]) -> str:
    """
    Подготавливает данные и собирает сообщения.
    """
    formatted_data = await prepare_pharmacy_data(data)
    messages = [await build_pharmacy_message(d) for d in formatted_data]
    return ''.join(messages)
