import requests
import json
from pprint import pprint
from datetime import datetime as dt

from sqlalchemy import create_engine, select, exists, update
from sqlalchemy.orm import Session

from models import Drug, Pharmacy, Pharmacy_drug
from utils import engine, create_DB

API_URL = 'https://gorzdrav.spb.ru/_api/api/v2/medication/pharmacies/search?'


def update_pharmacy_drug_counts(
        engine, pharmacy_id: int, drug_id: int, counts: dict
) -> None:
    with Session(engine) as session:
        query = update(Pharmacy_drug).where(
            Pharmacy_drug.pharmacy_id == pharmacy_id,
            Pharmacy_drug.drug_id == drug_id
        ).values(**counts)

        session.execute(query)
        session.commit()


def build_payload(name: str) -> dict:

    # name = str(input('Препарат ')).lower()

    payload = {
        "nom": name,
        "isLgot": "true",
    }

    return payload


def make_request(payload: dict) -> str:
    response = requests.get(
            API_URL,
            params=payload
        )

    return response.json()['result']


def write_data(response: str) -> None:
    for item in response:
        name = item['drugName']
        pharmacy_name = item['storeName']
        actuality_dt = dt.strptime(item['actualDate'], "%Y-%m-%dT%H:%M:%S")

        with Session(engine) as session:

            pharmacy_id = (select(Pharmacy.id)
                           .where(Pharmacy.name == pharmacy_name)
                           .scalar_subquery())

            drug_id = (select(Drug.id)
                       .where(
                            Drug.name == name,
                            Drug.dosage == item['dosage']
                    ).scalar_subquery())

            if not session.query(
                exists().where(Pharmacy.id == pharmacy_id)
            ).scalar():
                pharmacy = Pharmacy(
                    name=pharmacy_name,
                    phone=item['storePhone'],
                    subway=item['storeRoute'],
                    address=item['storeAddress']
                )

                session.add(pharmacy)
                session.commit()

            if not session.query(
                exists().where(Drug.id == drug_id)
            ).scalar():
                drug = Drug(
                    name=name,
                    dosage=item['dosage'],
                    сut_rate=item['isLgot'],
                    data_time=actuality_dt,
                    package=item['package']
                )
                session.add(drug)
                session.commit()

            association_exists = session.query(
                exists().where(
                    (Pharmacy_drug.pharmacy_id == pharmacy_id) &
                    (Pharmacy_drug.drug_id == drug_id)
                )
            ).scalar()

            if not association_exists:
                session.add(
                    Pharmacy_drug(
                        pharmacy_id=pharmacy_id,
                        drug_id=drug_id,
                        regional_count=0,
                        federal_count=0,
                        ssz_count=0,
                        psychiatry_count=0,
                        refugee_count=0
                    )
                )
                session.commit()

        counts = {
            'regional_count': item['regionalCount'],
            'federal_count': item['federalCount'],
            'ssz_count': item['sszCount'],
            'psychiatry_count': item['psychiatryCount'],
            'refugee_count': item['refugeeCount']
        }
        update_pharmacy_drug_counts(
            engine, pharmacy_id, drug_id, counts
        )
        session.commit()


def main():
    drug = 'пентаса'
    payload = build_payload(drug)
    response = make_request(payload)
    create_DB(engine)
    write_data(response)


if __name__ == '__main__':
    main()
