from sqlalchemy import create_engine, exists, update, select
from pathlib import Path
import os
from datetime import datetime as dt

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker

from models import Base, Drug, Pharmacy, Pharmacy_drug

BASE_DIR = Path(__file__).parent
DB_DIR = BASE_DIR / 'data'
DB_DIR.mkdir(exist_ok=True)

DB_PATH = os.path.abspath(DB_DIR / 'drugs.db')

async_engine = create_async_engine(f'sqlite+aiosqlite:///{DB_PATH}', echo=True)
async_session_factory = async_sessionmaker(async_engine)


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Tables created successfully.')


async def add_pharmacy(
    item: dict, pharmacy_name: str, pharmacy_id: int
) -> None:
    async with async_session_factory() as session:
        query = await session.execute(
                    select(Pharmacy.id)
                    .where(Pharmacy.id == pharmacy_id)
                )
        if not query.scalar():

            pharmacy = Pharmacy(
                name=pharmacy_name,
                phone=item['storePhone'],
                subway=item['storeRoute'],
                address=item['storeAddress'],
                #working_time=item['storeWorkingTime']
            )

            session.add(pharmacy)
            await session.commit()


async def add_drug(
        item: dict, drug_name: str, drug_id: int,
        pharmacy_id: int, actuality_dt: dt
) -> None:
    async with async_session_factory() as session:
        query = await session.execute(
                    select(Drug.id)
                    .where(Drug.id == drug_id)
                )
        if not query.scalar():
            drug = Drug(
                name=drug_name,
                dosage=item['dosage'],
                сut_rate=item['isLgot'],
                package=item['package']
            )
            session.add(drug)
            session.commit()

            association_exists = await session.execute(
                        select(Pharmacy_drug)
                        .where(
                            (Pharmacy_drug.pharmacy_id == pharmacy_id) &
                            (Pharmacy_drug.drug_id == drug_id)
                        )
                )

            if not association_exists.scalar():
                session.add(
                    Pharmacy_drug(
                        pharmacy_id=pharmacy_id,
                        drug_id=drug_id,
                        data_time=actuality_dt,
                        regional_count=0,
                        federal_count=0,
                        ssz_count=0,
                        psychiatry_count=0,
                        refugee_count=0
                    )
                )
                await session.commit()


async def update_pharmacy_drug_counts(
        pharmacy_id: int, drug_id: int, actuality_dt: dt,
        counters: dict
) -> None:
    """
    Обновляет каунтеры в аптеке по препарату
    """
    async with async_session_factory() as session:

        query = update(Pharmacy_drug).where(
            Pharmacy_drug.pharmacy_id == pharmacy_id,
            Pharmacy_drug.drug_id == drug_id,
            Pharmacy_drug.data_time == actuality_dt
        ).values(**counters)

        await session.execute(query)
        await session.commit()
