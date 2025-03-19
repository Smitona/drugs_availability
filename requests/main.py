import requests
from sqlalchemy import create_engine, select
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


def write_data(name: str):
    name = build_payload()['nom']
    engine = create_engine("postgresql://", echo=True)

    with Session(engine) as session:

        drug_in_DB = (
            select(Drug)
            .where(Drug.name == name)
        )
        if drug_in_DB.exists() is False:
            

            session.add_all()

        session.commit()


def main():
    payload = build_payload()
    make_request(payload)


if __name__ == '__main__':
    main()
