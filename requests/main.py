import requests
from sqlalchemy import create_engine, select, exists
from sqlalchemy.orm import Session

from models import Drug

API_URL = 'https://gorzdrav.spb.ru/_api/api/v2/medication/pharmacies/search?'


def build_payload() -> dict:

    name = str(input('Препарат ')).lower()

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

    response_json = response.json()

    return response_json['result']


def write_data(response: str) -> None:
    name = build_payload()['nom']
    engine = create_engine("postgresql://", echo=True)

    with Session(engine) as session:

        drug_in_DB = select(Drug.id).where(Drug.name == name)

        if select(Drug).where(exists(drug_in_DB)) is False:
            drug = Drug(
                name=name,
                dosage=response['dosage'],
                сut_rate=response['сut_rate'],
                data_time=response['data_time'],
                package=response['package']
            )
            session.add(drug)
            session.commit()

        session.commit()


def main():
    payload = build_payload()
    make_request(payload)


if __name__ == '__main__':
    main()
