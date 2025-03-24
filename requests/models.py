from sqlalchemy import (
    Column, Integer, String, Boolean, Interval, DateTime, Table, ForeignKey
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

pharmacy_drug_association = Table(
    'pharmacy_drug_association',
    Base.metadata,
    Column('pharmacy_id', ForeignKey('pharmacies.id')),
    Column('drug_id', ForeignKey('drugs.id')),
    Column('regional_сount', Integer, nullable=False, default=0),
    Column('federal_count', Integer, nullable=False, default=0),
    Column('ssz_count', Integer, nullable=False, default=0),
    Column('psychiatry_count', Integer, nullable=False, default=0),
    Column('refugee_count', Integer, nullable=False, default=0)
)


class Pharmacy(Base):
    __tablename__ = 'pharmacies'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    working_time = Column(Interval)
    phone = Column(String)
    subway = Column(String)
    name = Column(String)
    address = Column(String)
    drugs = relationship(
        'Drug', secondary=pharmacy_drug_association, back_populates='pharmacy'
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
    name = Column(String, nullable=False, unique=True)
    dosage = Column(String)
    сut_rate = Column(Boolean, server_default='true', nullable=False)
    data_time = Column(DateTime)
    package = Column(String)
    pharmacy = relationship(
        'Pharmacy', secondary=pharmacy_drug_association, back_populates='drugs'
    )
    users = relationship(
        'User', secondary=user_drug_association, back_populates='drugs'
    )
