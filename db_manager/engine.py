from sqlmodel import create_engine
from sqlmodel import Session
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True, max_overflow=50,
    pool_size=100,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,)

def get_session():
    return session

session = Session(engine)

