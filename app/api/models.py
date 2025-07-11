from datetime import datetime
from typing import Dict
from sqlalchemy import ForeignKey, UniqueConstraint, JSON, Index
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
#from sqlalchemy.dialects.postgresql import JSONB


class Base(DeclarativeBase):
    pass


class User_drug(Base):
    __tablename__ = 'user_drug'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), primary_key=True
    )
    drug_id: Mapped[int] = mapped_column(
        ForeignKey('drugs.id'), primary_key=True
    )


class Pharmacy_drug(Base):
    __tablename__ = 'pharmacy_drug'

    pharmacy_id: Mapped[int] = mapped_column(
        ForeignKey('pharmacies.id'), primary_key=True
    )
    drug_id: Mapped[int] = mapped_column(
        ForeignKey('drugs.id'), primary_key=True
    )
    data_time: Mapped[datetime]
    regional_count: Mapped[int] = mapped_column(nullable=False, default=0)
    federal_count: Mapped[int] = mapped_column(nullable=False, default=0)
    ssz_count: Mapped[int] = mapped_column(nullable=False, default=0)
    psychiatry_count: Mapped[int] = mapped_column(nullable=False, default=0)
    refugee_count: Mapped[int] = mapped_column(nullable=False, default=0)
    diabetic_kids_2_4_count: Mapped[int] = mapped_column(nullable=False, default=0)
    diabetic_kids_4_17_count: Mapped[int] = mapped_column(nullable=False, default=0)
    hepatitis_count: Mapped[int] = mapped_column(nullable=False, default=0)

    __table_args__ = (
        Index('idx_drug_id', 'drug_id'),
        Index(
            'idx_counters',
            'regional_count', 'federal_count', 'ssz_count',
            'psychiatry_count', 'refugee_count', 'diabetic_kids_2_4_count',
            'diabetic_kids_4_17_count', 'hepatitis_count'
        ),
        Index('idx_pharmacy_drug', 'drug_id', 'pharmacy_id')
    )


class Pharmacy(Base):
    """
    Модель аптек.

        name — название с номером
        working_time - рабочие часы
        phone — номер аптеки
        subway — метро, ближайшее к аптеке
        address — адрес аптеки
        district — район СПб
        route — путь до аптеки от метро, включая транспорт
        drugs — препараты, которые бывают в этой аптеке
    """
    __tablename__ = 'pharmacies'

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True
    )
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    working_time: Mapped[Dict[str, str]] = mapped_column(JSON, nullable=True)
    phone: Mapped[str]
    subway: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str] = mapped_column(unique=True, nullable=False)
    district: Mapped[str] = mapped_column(unique=True, nullable=False)
    route: Mapped[str] = mapped_column(nullable=False)
    drugs: Mapped[list['Drug']] = relationship(
        'Drug', secondary='pharmacy_drug', back_populates='pharmacy'
    )


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True
    )
    telegram_id: Mapped[int] = mapped_column(unique=True)
    drugs: Mapped[list['Drug']] = relationship(
        'Drug', secondary='user_drug', back_populates='users'
    )


class Drug(Base):
    __tablename__ = 'drugs'

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True
    )
    name: Mapped[str] = mapped_column(nullable=False)
    dosage: Mapped[str] = mapped_column(nullable=False)
    form: Mapped[str] = mapped_column(nullable=False)
    numero: Mapped[str] = mapped_column(nullable=False)
    pharmacy: Mapped[list['Pharmacy']] = relationship(
        'Pharmacy', secondary='pharmacy_drug', back_populates='drugs'
    )
    users: Mapped[list['User']] = relationship(
        'User', secondary='user_drug', back_populates='drugs'
    )

    __table_args__ = (
        UniqueConstraint('name', 'dosage', name='uq_drug_name_dosage'),
        Index('idx_id', 'id'),
        Index('idx_name_pattern', 'name')
        #Index(
           # 'idx_drug_name_gin_trgm',
          #  text(text("name gin_trgm_ops"),  # Для PostgreSQL
           # postgresql_using='gin'
        #),
    )
