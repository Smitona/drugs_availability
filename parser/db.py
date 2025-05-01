from sqlalchemy import create_engine, exists, update, select
from pathlib import Path
import os
import re
from datetime import datetime as dt

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
    AsyncSession
from sqlalchemy.orm import Session, sessionmaker

from models import Base, Drug, Pharmacy, Pharmacy_drug, User_drug
from utils import parse_schedule

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
            working_time = parse_schedule(item['storeWorkingTime'])

            pharmacy = Pharmacy(
                name=pharmacy_name,
                working_time=working_time,
                phone=item['storePhone'],
                subway=item['storeRoute'],
                address=item['storeAddress'],
                district=item['storeDistrict'],
                route=item['storeRoute']
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
            package = re.search(r'№(\d+)', item['package']).group(1)

            drug = Drug(
                name=drug_name,
                dosage=item['dosage'],
                сut_rate=item['isLgot'],
                numero=package,
                form=item['formOf']
            )
            session.add(drug)
            await session.commit()

            association_exists = await session.execute(
                        select(Pharmacy_drug)
                        .where(
                            (Pharmacy_drug.pharmacy_id == pharmacy_id) &
                            (Pharmacy_drug.drug_id == drug_id)
                        )
                )

            if not association_exists.scalar():
                await session.add(
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
    Обновляет каунтеры в аптеке по препарату.

    pharmacy_id: id аптеки в БД
    drug_id: id препарата в БД
    actuality_dt: дата обновленя информации по количеству, значение из API
    counters: словарь с количеством препарата в аптеке по разным льготам
    """
    async with async_session_factory() as session:

        query = update(Pharmacy_drug).where(
            Pharmacy_drug.pharmacy_id == pharmacy_id,
            Pharmacy_drug.drug_id == drug_id,
            Pharmacy_drug.data_time == actuality_dt
        ).values(**counters)

        await session.execute(query)
        await session.commit()


async def save_favorite_drug(
        telegram_id: int, drug_id: int
) -> None:
    """
    Сохраняет связь пользователь—id препарата в БД.

    telegram_id: id чата в Телеграмме
    drug_id: id препарата в БД
    """
    async with async_session_factory() as session:
        fav_drug = User_drug(
            user_id=telegram_id,
            drug_id=drug_id
        )
        session.add(fav_drug)
        await session.commit()


async def get_favorite_drug(telegram_id: int) -> list:
    """
    Забирает из БД связь telegram_id и списка препаратов по id.
    Показывает на кнопках названия препаратов и дозировку
    select drug.name и drug.dosage
    """
    # callback.chat.id -> telegram_id

    async with async_session_factory() as session:
        query = await session.execute(
            select(Drug.name, Drug.dosage)
            .join(User_drug, User_drug.drug_id == Drug.id)
            .where(User_drug.user_id == telegram_id)
        )

        fav_drugs = await query.all()

        return fav_drugs
