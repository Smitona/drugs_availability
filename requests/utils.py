from sqlalchemy import create_engine
import psycopg2

from models import Base


def create_sql_engine():
    DB_URL = 'sqlite:///drugs_db'
    engine = create_engine(DB_URL, echo=True)
    print(len(DB_URL))

    return engine


engine = create_sql_engine()


def create_DB(engine):
    Base.metadata.create_all(engine)
    print('Table "employees" created successfully.')

