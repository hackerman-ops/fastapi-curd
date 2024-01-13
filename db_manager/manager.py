from typing import Any, List

from sqlmodel import select, Session
from db_manager.db_models import Company
from db_manager.engine import engine
from sqlalchemy import delete, update

class DBManager:
    def __init__(self, engine):
        self.engine = engine

    def create_one(self, model_data):
        with Session(self.engine) as session:
            session.add(model_data)
            session.commit()
            session.refresh(model_data)
            return model_data

    def get_one(self, model, model_id):
        with Session(engine) as session:
            sql = select(model).where(model.id == model_id)
            return session.scalars(sql).first()
    
    def delete_one(self, model, model_id):
        with Session(self.engine) as session:
            statement = delete(model).where(model.id == model_id)
            session.exec(statement)
            session.commit()
    
    def update_one(self, model, model_id, **kwargs):
        with Session(self.engine) as session:
            statement = update(model).where(model.id == model_id).values(**kwargs)
            session.exec(statement)
            session.close()
    
    def get_multi(self, model,**kwargs):
        with Session(self.engine) as session:
            select_statement = select(model).filter_by(**kwargs)
            return session.exec(select_statement).all()
    def delete_multi(self, model, **kwargs):
        with Session(self.engine) as session:
            statement = delete(model).filter_by(**kwargs)
            session.exec(statement)
            session.commit()

    def update_multi(self, model,filter, **kwargs):
        with Session(self.engine) as session:
            statement = update(model).filter_by(**filter).values(**kwargs)
            session.exec(statement)
            session.commit()

    def get_count(self, model, **kwargs):
        from sqlalchemy.sql.expression import func

        with Session(self.engine) as session:
            select_statement = select(func.count("*")).select_from(model).filter_by(**kwargs)
            return session.exec(select_statement).one()
db_manager = DBManager(engine)


if __name__ == "__main__":
    f = db_manager.get_multi(Company, name="new name")
    print(f)