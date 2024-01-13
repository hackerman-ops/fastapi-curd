from typing import Any, List
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlmodel import select
from db_manager.db_models import Company
from db_manager.async_engine import engine
from db_manager.async_engine import AsyncSession
from sqlalchemy import delete, update

class AsyncDBManager:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def create_one(self, model_data):
        self.session.add(model_data)
        await self.session.commit()
        await self.session.refresh(model_data)
        return model_data

    async def get_one(self, model, model_id):
        sql = select(model).where(model.id == model_id)
        result = await self.session.exec(sql)
        return result.scalars().first()
    
    async def delete_one(self, model, model_id):
        statement = delete(model).where(model.id == model_id)
        await self.session.exec(statement)
        await self.session.commit()
    
    async def update_one(self, model, model_id, **kwargs):
        statement = update(model).where(model.id == model_id).values(**kwargs)
        await self.session.exec(statement)
        await self.session.commit()
    
    async def get_multi(self, model,**kwargs):
        select_statement = select(model).filter_by(**kwargs)
        result = await self.session.exec(select_statement)
        return result.all()
    async def delete_multi(self, model, **kwargs):
        statement = delete(model).filter_by(**kwargs)
        await self.session.exec(statement)
        await self.session.commit()

    async def update_multi(self, model,filter, **kwargs):
        statement = update(model).filter_by(**filter).values(**kwargs)
        await self.session.exec(statement)
        await self.session.commit()

    async def get_count(self, model, **kwargs):
        from sqlalchemy.sql.expression import func

        select_statement = select(func.count("*")).select_from(model).filter_by(**kwargs)
        result = await self.session.exec(select_statement)
        return result.one()
db_manager = AsyncDBManager(engine)


if __name__ == "__main__":
    f = db_manager.get_multi(Company, name="new name")
    print(f)