from sqlalchemy import create_engine, exists, update
from pathlib import Path
import os
from datetime import datetime as dt

from sqlalchemy.orm import Session

from .models import Base, Drug, Pharmacy, Pharmacy_drug

BASE_DIR = Path(__file__).parent
DB_DIR = BASE_DIR / 'data'
DB_DIR.mkdir(exist_ok=True)


def create_sql_engine():
    DB_PATH = os.path.abspath(DB_DIR / 'drugs.db')
    engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)

    return engine


engine = create_sql_engine()


def create_DB(engine) -> None:
    Base.metadata.create_all(engine, checkfirst=True)
    print('Tables created successfully.')


def add_pharmacy(
        session, item: dict, pharmacy_name: str, pharmacy_id: int
) -> None:
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


def add_drug(
        session, item: dict, drug_name: str, drug_id: int, pharmacy_id: int
) -> None:
    if not session.query(
                exists().where(Drug.id == drug_id)
            ).scalar():
        drug = Drug(
            name=drug_name,
            dosage=item['dosage'],
            сut_rate=item['isLgot'],
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


def update_pharmacy_drug_counts(
        engine, pharmacy_id: int, drug_id: int, actuality_dt: dt,
        counters: dict
) -> None:
    with Session(engine) as session:
        query = update(Pharmacy_drug).where(
            Pharmacy_drug.pharmacy_id == pharmacy_id,
            Pharmacy_drug.drug_id == drug_id,
            Pharmacy_drug.data_time == actuality_dt
        ).values(**counters)

        session.execute(query)
        session.commit()
