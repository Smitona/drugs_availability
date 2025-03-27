import requests
import time
from datetime import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Drug, Pharmacy
from utils import (
    engine, create_DB, add_pharmacy, update_pharmacy_drug_counts, add_drug
)

API_URL = 'https://gorzdrav.spb.ru/_api/api/v2/medication/pharmacies/search?'


def make_request(name: str) -> str:
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
    except KeyError:
        time.sleep(5)
        result = response.json()['result']

    return result


def write_data(response: str) -> None:
    for item in response:
        drug_name = item['drugName']
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


def main():
    drug = 'ранвэк'
    response = make_request(drug)
    create_DB(engine)
    write_data(response)


if __name__ == '__main__':
    main()
