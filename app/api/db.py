from sqlalchemy import update, select, and_, or_
import os
import re
from datetime import datetime as dt
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.api.models import Base, Drug, Pharmacy, Pharmacy_drug, User_drug
from app.api.utils import parse_schedule

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
    session, item: dict, pharmacy_name: str
) -> int:
    working_time = await parse_schedule(item['storeWorkingTime'])
    phone = item['storePhone'].replace("-", "")

    pharmacy = Pharmacy(
        name=pharmacy_name,
        working_time=working_time,
        phone=phone,
        subway=item['storeSubway'],
        address=item['storeAddress'],
        district=item['storeDistrict'],
        route=item['storeRoute']
    )

    session.add(pharmacy)
    await session.flush()

    return pharmacy.id


async def add_drug(
        session, item: dict, drug_name: str
) -> int:
    package = re.search(r'№(\d+)', item['package']).group(1)

    drug = Drug(
        name=drug_name.lower(),
        dosage=item['dosage'],
        numero=package,
        form=item['formOf']
    )
    session.add(drug)

    await session.flush()

    return drug.id


async def update_pharmacy_drug_counts(
        session, pharmacy_id: int, drug_id: int,
        actuality_dt: dt, counters: dict
) -> None:
    """
    Обновляет каунтеры в аптеке по препарату.

    pharmacy_id: id аптеки в БД
    drug_id: id препарата в БД
    actuality_dt: дата обновленя информации по количеству, значение из API
    counters: словарь с количеством препарата в аптеке по разным льготам
    """

    ass = await session.execute(
        select(Pharmacy_drug).where(
            Pharmacy_drug.pharmacy_id == pharmacy_id,
            Pharmacy_drug.drug_id == drug_id
        )
    )

    ass_exists = ass.scalar_one_or_none()

    if not ass_exists:
        session.add(
            Pharmacy_drug(
                pharmacy_id=pharmacy_id,
                drug_id=drug_id,
                data_time=actuality_dt,
                **counters
            )
        )

    else:
        for field, value in counters.items():
            setattr(ass_exists, field, value)
            ass_exists.data_time = actuality_dt


async def return_data_from_DB(
    drug_id: int
) -> dict:
    """
    Отдаёт данные из БД для польза.

        Принимает

        drug_id: препарата

        Возвращает:

        Каунтеры препарата в аптеках с заданной дозировкой dosage.
    """
    async with async_session_factory() as session:

        if drug_id:
            query = (
                select(Pharmacy, Pharmacy_drug)
                .join(
                    Pharmacy,
                    Pharmacy_drug.pharmacy_id == Pharmacy.id
                )
                .where(
                    and_(
                        Pharmacy_drug.drug_id == drug_id,
                        or_(
                            Pharmacy_drug.regional_count > 0,
                            Pharmacy_drug.federal_count > 0,
                            Pharmacy_drug.ssz_count > 0,
                            Pharmacy_drug.refugee_count > 0,
                            Pharmacy_drug.diabetic_kids_2_4_count > 0,
                            Pharmacy_drug.diabetic_kids_4_17_count > 0,
                            Pharmacy_drug.hepatitis_count > 0
                        )
                    )
                )
            )
            result = await session.execute(query)
            counters = result.all()

        found_pharmacies = []
        for pharmacy, pharmacy_drug in counters:
            found_pharmacies.append({
                'pharm_name': pharmacy.name,
                'pharm_phone': pharmacy.phone,
                'pharm_district': pharmacy.district,
                'pharm_subway': pharmacy.subway,
                'pharm_loc': pharmacy.address,
                'pharm_route': pharmacy.route,
                'pharm_work': pharmacy.working_time,
                'last_update': pharmacy_drug.data_time,
                'regional': pharmacy_drug.regional_count,
                'federal': pharmacy_drug.federal_count,
                'ssz': pharmacy_drug.ssz_count,
                'refugee': pharmacy_drug.refugee_count,
                'diabetic_kids_2_4': pharmacy_drug.diabetic_kids_2_4_count,
                'diabetic_kids_4_17': pharmacy_drug.diabetic_kids_4_17_count,
                'hepatitis': pharmacy_drug.hepatitis_count
            })

        return found_pharmacies


async def forms_from_DB(drug_name: str) -> list:
    async with async_session_factory() as session:
        query = select(Drug).where(
            Drug.name.ilike(f'%{drug_name}%')
        )
        #text("name % :pattern")  # Оператор % из pg_trgm
        #).params(pattern=f"%{drug_name}%")

        result = await session.execute(query)
        drugs = result.scalars().all()

        found_drugs = []
        for drug in drugs:
            found_drugs.append({
                'id': drug.id,
                'name': drug.name,
                'dosage': drug.dosage,
                'form': drug.form,
                'numero': drug.numero
            })

        return found_drugs


async def save_favorite_drug(
        telegram_id: int, drug_id: int
) -> bool:
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
    return True


async def is_favorite_drug(user_id: int, drug_id: int) -> None:
    async with async_session_factory() as session:
        query = (
            select(User_drug)
            .where(
                and_(
                    User_drug.user_id == user_id,
                    User_drug.drug_id == drug_id
                )
            )
        )

        fav_drugs = await session.execute(query)
        result = fav_drugs.scalar_one_or_none()

        return result


async def get_favorite_drugs(telegram_id: int) -> list:
    """
    Забирает из БД связь telegram_id и списка препаратов по id.
    Показывает на кнопках названия препаратов и дозировку
    select drug.name и drug.dosage
    """
    # callback.chat.id -> telegram_id

    async with async_session_factory() as session:
        query = (
            select(Drug)
            .join(User_drug, User_drug.drug_id == Drug.id)
            .where(User_drug.user_id == telegram_id)
        )
        result = await session.execute(query)
        fav_drugs = result.scalars().all()

        fav_drugs_list = []
        for drug in fav_drugs:
            fav_drugs_list.append({
                'id': drug.id,
                'name': drug.name,
                'dosage': drug.dosage,
                'form': drug.form,
                'numero': drug.numero
            })

        return fav_drugs_list
