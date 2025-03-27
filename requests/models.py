from sqlalchemy import (
    Column, Integer, String, Boolean, Interval,
    DateTime, Table, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base 

Base = declarative_base()

user_drug_association = Table(
    'user_drug_association',
    Base.metadata,
    Column('user_id', ForeignKey('users.id')),
    Column('drug_id', ForeignKey('drugs.id')),
)


class Pharmacy_drug(Base):
    __tablename__ = 'pharmacy_drug'

    pharmacy_id = Column(
        Integer, ForeignKey('pharmacies.id'), primary_key=True
    )
    drug_id = Column(
        Integer, ForeignKey('drugs.id'), primary_key=True
    )
    data_time = Column(DateTime)
    regional_count = Column(Integer, nullable=False, default=0)
    federal_count = Column(Integer, nullable=False, default=0)
    ssz_count = Column(Integer, nullable=False, default=0)
    psychiatry_count = Column(Integer, nullable=False, default=0)
    refugee_count = Column(Integer, nullable=False, default=0)


class Pharmacy(Base):
    __tablename__ = 'pharmacies'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    working_time = Column(Interval)
    phone = Column(String)
    subway = Column(String)
    name = Column(String, unique=True)
    address = Column(String)
    drugs = relationship(
        'Drug', secondary='pharmacy_drug', back_populates='pharmacy'
    )


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    telegram_id = Column(Integer)
    drugs = relationship(
        'Drug', secondary=user_drug_association, back_populates='users'
    )


class Drug(Base):
    __tablename__ = 'drugs'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    сut_rate = Column(Boolean, server_default='true', nullable=False)
    package = Column(String)
    pharmacy = relationship(
        'Pharmacy', secondary='pharmacy_drug', back_populates='drugs'
    )
    users = relationship(
        'User', secondary=user_drug_association, back_populates='drugs'
    )

    __table_args__ = (
        UniqueConstraint('name', 'dosage', name='uq_drug_name_dosage'),
    )
