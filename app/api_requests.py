import requests
import re
import time
from datetime import datetime as dt

from sqlalchemy import select

from models import Drug, Pharmacy
from db import async_session_factory, add_pharmacy, add_drug, \
    update_pharmacy_drug_counts
from utils import prepare_drug_data


API_URL = 'https://gorzdrav.spb.ru/_api/api/v2/medication/pharmacies/search?'


async def make_request(name: str) -> str:
    """
    Делает запрос в API и обрабатывает возможные ответы.
    """
    payload = {
        "nom": name,
        "isLgot": "true",
    }

    response = requests.get(
            API_URL,
            params=payload,
            timeout=(2, 5)
        )

    try:
        result = response.json()['result']
    except Exception:
        print('Актуальные данные недоступны.', response.json()['message'])
        result = response.json()['message']
    except KeyError:
        await time.sleep(5)
        result = response.json()['result']

    return result


async def write_data(response: str) -> None:
    """
    Записывает данные в БД по препаратам, используя данные из API.
    """

    for item in response:
        drug_name, pharmacy_name, actuality_dt = await prepare_drug_data(item)

        async with async_session_factory() as session:
            pharmacy_result = await session.execute(
                select(Pharmacy.id).where(Pharmacy.name == pharmacy_name)
            )
            pharmacy_id = pharmacy_result.scalar()

            if not pharmacy_id:
                await add_pharmacy(item, pharmacy_name)
                pharmacy_result = await session.execute(
                    select(Pharmacy.id).where(Pharmacy.name == pharmacy_name)
                )
                pharmacy_id = pharmacy_result.scalar()

            drug_result = await session.execute(
                    select(Drug.id).where(
                        Drug.name == drug_name.lower(),
                        Drug.dosage == item['dosage']
                    )
                )
            drug_id = drug_result.scalar()

            if not drug_id:
                drug_id = await add_drug(
                    item, drug_name, pharmacy_id, actuality_dt
                )

        counters = {
            'regional_count': item['regionalCount'],
            'federal_count': item['federalCount'],
            'ssz_count': item['sszCount'],
            'psychiatry_count': item['psychiatryCount'],
            'refugee_count': item['refugeeCount'],
            'diabetic_kids_2_4_count': item['diabeticKids24Count'],
            'diabetic_kids_4_17_count': item['diabeticKids417Count'],
            'hepatitis_count': item['hepatitisCount']
        }
        await update_pharmacy_drug_counts(
            pharmacy_id, drug_id, actuality_dt, counters
        )
