import requests
import time
from datetime import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Drug, Pharmacy
from .utils import engine, add_pharmacy, \
    update_pharmacy_drug_counts, add_drug


API_URL = 'https://gorzdrav.spb.ru/_api/api/v2/medication/pharmacies/search?'


def make_request(name: str) -> str:
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
        time.sleep(5)
        result = response.json()['result']

    return result


def write_data(response: str) -> None:
    """
    Записывает данные в БД по препаратам.
    """
    for item in response:
        full_name = item['drugName']
        drug_name = full_name.split()[0]
        pharmacy_name = item['storeName']
        actuality_dt = dt.strptime(item['actualDate'], "%Y-%m-%dT%H:%M:%S")

        with Session(engine) as session:

            pharmacy_id = (select(Pharmacy.id)
                           .where(Pharmacy.name == pharmacy_name)
                           .scalar_subquery())

            drug_id = (select(Drug.id)
                       .where(
                            Drug.name == drug_name,
                            Drug.dosage == item['dosage']
                    ).scalar_subquery())

            add_pharmacy(
                session, item, pharmacy_name, pharmacy_id
            )

            add_drug(
                session, item, drug_name, drug_id
            )

        counters = {
            'regional_count': item['regionalCount'],
            'federal_count': item['federalCount'],
            'ssz_count': item['sszCount'],
            'psychiatry_count': item['psychiatryCount'],
            'refugee_count': item['refugeeCount']
        }
        update_pharmacy_drug_counts(
            engine, pharmacy_id, drug_id, actuality_dt, counters
        )
        session.commit()


def return_data_from_DB(drug_id: int) -> dict:
    """
    Отдаёт данные из Бд для польза.
    name - название препарата
    dosage - дозировка
    pharmacy - аптека
    """
    with Session(engine) as session:
        query = (
            select(Drug)
            .where(Drug.id == drug_id)
            .first()
        )

        drug = session.execute(query)

        return {
            'name': drug.name,
            'dosage': drug.dosage,
            'pharmacy': drug.pharmacy
        }

