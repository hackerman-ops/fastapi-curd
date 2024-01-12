from sqlmodel import create_engine
from models import SQLModel

sqlite_file_name = "database1.db"
sqlite_url = "postgresql+psycopg2://my_user:password123@172.30.167.162:5433/sql_model"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # SQLModel.metadata.drop_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
