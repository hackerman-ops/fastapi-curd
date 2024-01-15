from sqlmodel import create_engine
from sqlmodel import Session

pg_url = "postgresql+psycopg2://my_user:password123@172.30.167.162:5433/sql_model"

engine = create_engine(
    pg_url,
    echo=True,
    max_overflow=50,
    pool_size=100,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)


def get_session():
    return session


session = Session(engine)
