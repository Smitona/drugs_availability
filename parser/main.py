import requests
import time
import asyncio
from datetime import datetime as dt

from sqlalchemy import select

from models import Drug, Pharmacy
from utils import async_session_factory, create_tables, \
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

    # Подумать над add_all
    for item in response:
        full_name = item['drugName']
        drug_name = full_name.split()[0]
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
            'refugee_count': item['refugeeCount']
        }
        await update_pharmacy_drug_counts(
            pharmacy_id, drug_id, actuality_dt, counters
        )


async def return_data_from_DB(drug_id: int) -> dict:
    """
    Отдаёт данные из Бд для польза.
    name - название препарата
    dosage - дозировка
    pharmacy - аптека
    """
    with async_session_factory() as session:
        query = (
            select(Drug)
            .where(Drug.id == drug_id)
            .first()
        )

        drug = await session.execute(query)

        return {
            'name': drug.name,
            'dosage': drug.dosage,
            'pharmacy': drug.pharmacy
        }


async def main() -> None:
    await create_tables()
    response = await make_request('пентаса')
    await write_data(response)


if __name__ == "__main__":
    asyncio.run(main())
