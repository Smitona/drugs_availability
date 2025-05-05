import requests
import re
import time
import asyncio
from datetime import datetime as dt

from sqlalchemy import select

from models import Drug, Pharmacy
from db import async_session_factory, create_tables, \
    add_pharmacy, update_pharmacy_drug_counts, add_drug


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
            params=payload
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
    Записывает данные в БД по препаратам.
    """

    for item in response:
        full_name = item['drugName']

        match = re.search(r'^(\w+)[®, ]', full_name)

        if match:
            drug_name = match.group(1)
        else:
            drug_name = full_name.split()[0] if full_name else ""

        pharmacy_name = item['storeName']
        actuality_dt = dt.strptime(item['actualDate'], "%Y-%m-%dT%H:%M:%S")

        pharmacy_id = (select(Pharmacy.id)
                       .where(Pharmacy.name == pharmacy_name)
                       .scalar_subquery())

        drug_id = (select(Drug.id)
                   .where(
                       Drug.name == drug_name,
                       Drug.dosage == item['dosage']
                ).scalar_subquery())

        await add_pharmacy(item, pharmacy_name, pharmacy_id)

        await add_drug(item, drug_name, drug_id, pharmacy_id, actuality_dt)

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


async def main() -> None:
    await create_tables()
    response = await make_request('далибра')
    await write_data(response)


if __name__ == "__main__":
    asyncio.run(main())
