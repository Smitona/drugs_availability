from datetime import datetime
from typing import Dict
from sqlalchemy import ForeignKey, UniqueConstraint, JSON
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


class Pharmacy(Base):
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
    сut_rate: Mapped[bool] = mapped_column(
        server_default='true', nullable=False
    )
    form: Mapped[str] = mapped_column(nullable=False)
    numero: Mapped[str]
    pharmacy: Mapped[list['Pharmacy']] = relationship(
        'Pharmacy', secondary='pharmacy_drug', back_populates='drugs'
    )
    users: Mapped[list['User']] = relationship(
        'User', secondary='user_drug', back_populates='drugs'
    )

    __table_args__ = (
        UniqueConstraint('name', 'dosage', name='uq_drug_name_dosage'),
    )
