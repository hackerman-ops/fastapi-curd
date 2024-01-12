from typing import Any, List

from sqlmodel import select, Session
from test_scripts.models import Company
from test_scripts.engine import engine
from sqlalchemy import delete, update

def create_heroes():
    hero_1 = Company(name="Dead2p2ond", email="Div2e Wilson", account=3, number=2)
    hero_2 = Company(name="Spide22r-Boy", email="Pedr2o Parqueador", account=4, number=4)
    hero_3 = Company(name="Rusty2-2Man", email="To2mmy Sharp", account=68, number=1000)
    with Session(engine) as session:
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        
        session.commit()
        session.refresh(hero_1)
        print(hero_1)



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
            sql = select(model).where(model.id == model_id)
            return session.scalars(sql).first()

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
from test_scripts.engine import engine

db_manager = DBManager(engine)


if __name__ == "__main__":
    # create_heroes()
    f = db_manager.get_count(Company, id=2)
    print(f)