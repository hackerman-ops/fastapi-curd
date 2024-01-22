import traceback
from typing import Any, Callable, Dict, List, Optional, Literal

from fastapi import BackgroundTasks
from fastapi import Depends, HTTPException
from fastapi import Request
from openpyxl import Workbook
from fastapi.responses import FileResponse
from fastapi_pagination.ext.sqlalchemy import paginate as fastapi_paginate
from pydantic import create_model
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import DeclarativeMeta as Model
from sqlmodel import select, update, delete
from db_manager.async_engine import get_session
from ._base import CRUDGenerator, NOT_FOUND
from .curd_types import PYDANTIC_SCHEMA as SCHEMA
from .curd_types import DBSchemas, RouteBackgrounds, RouteDependencies
from ._utils import (
    get_pk_type,
    create_filter_model_from_db_model_include_columns,
    QuerySqlGenerator,
)
from .curd_types import QueryAllParamsModel, CurrentUserPair, CustomParams, QueryParams


CALLABLE = Callable[..., Model]
CALLABLE_LIST = Callable[..., List[Model]]


class AsyncCRUDRouter(CRUDGenerator[SCHEMA]):
    def __init__(
        self,
        schemas: DBSchemas,
        route_dependencies: RouteDependencies,
        route_backgrounds: RouteBackgrounds,
        query_params: QueryAllParamsModel,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        current_user_pair: CurrentUserPair = None,
        **kwargs: Any,
    ) -> None:
        self.user_model = current_user_pair.user_model
        auth_info_func = current_user_pair.auth_info_func
        self.auth_info = Depends(auth_info_func) if auth_info_func else Depends()
        db_model = schemas.db_schema
        self.db_model = db_model
        self.schema = db_model
        self.create_schema = schemas.create_schema
        self.update_schema = schemas.update_schema
        self.session = AsyncSession
        self.query_model = QueryParams
        self.route_backgrounds = route_backgrounds
        self.pk: str = db_model.__table__.primary_key.columns.keys()[0]
        self.pk_type: type = get_pk_type(db_model, self.pk)
        self.filter_cfg = query_params.filter_cfg
        self.filter_model = None
        self.generate_filter_model()
        self.default_query_kwargs = query_params.default_query_kwargs
        self.default_sort_kwargs = query_params.default_sort_kwargs or {}
        super().__init__(
            schemas=schemas,
            prefix=prefix or db_model.__tablename__,
            tags=tags,
            route_dependencies=route_dependencies,
            **kwargs,
        )

    # 生成查询参数
    def generate_filter_model(self):
        if not self.filter_cfg:
            return
        mapping_list = []
        for co in self.filter_cfg:
            real_name = co.real_name
            mapping = {
                "new_key": co.key,
                "db_key": co.real_name if real_name else co.key,
            }
            mapping_list.append(mapping)
        self.filter_model = create_filter_model_from_db_model_include_columns(
            name_suffix="Create",
            model=self.schema,
            include=mapping_list,
            is_update=True,
        )
        self.query_model = create_model(
            f"{self.schema.__name__}Filter",
            filter=(self.filter_model, ...),
            __base__=QueryParams,
        )
    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            query_params: self.query_model,
            db: AsyncSession = Depends(self.session),
        ) -> List[Model]:
            filter_data = query_params.filter
            sorter_data = query_params.sorter
            sql_generator = QuerySqlGenerator(
                model=self.schema,
                user_query_data=filter_data.model_dump() if filter_data else None,
                default_query_data=self.default_query_kwargs,
                user_sort_data=sorter_data,
                default_sort_data=self.default_sort_kwargs,
                filter_setting=self.filter_cfg,
            )
            sql_generator.generate_query_record_sql()
            sql = sql_generator.query_sql
            pagination = query_params.pagination
            pagination = CustomParams(page=pagination.page, size=pagination.size)
            page_data = await fastapi_paginate(
                query=sql,
                params=pagination,  # type: ignore
                conn=db,  # type: ignore
            )  # type: ignore
            data_list = [
                self.schema.model_validate(item).model_dump()
                for item in page_data.items
            ]
            page_data.items = data_list
            return {"data": page_data}  # type: ignore

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self.pk_type, db: AsyncSession = Depends(self.session)  # type: ignore
        ):
            sql = select(self.db_model).where(self.db_model.id == item_id)
            result = await db.exec(sql)
            model = result.scalars().first()
            if not model:
                raise NOT_FOUND
            data = model.model_dump()
            return {"data": data}  # type: ignore

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.create_schema,  # type: ignore
            request: Request,
            background_tasks: BackgroundTasks,
            db: AsyncSession = Depends(self.session),
            current_user: self.user_model = self.auth_info,
        ):
            self.create_schema.model_validate(model)
            create_data = model.model_dump(exclude_unset=True, exclude_none=True)

            db_model = self.db_model(**create_data)
            print("======start=====")
            try:
                await db.add(db_model)
                await db.commit()
            except IntegrityError as e:
                traceback.print_exc()
                await db.rollback()
                raise HTTPException(422, "Key already exists")
            print("======end=======")
            db.refresh(db_model)

            data = self.schema.model_validate(db_model).model_dump()

            # 创建后执行任务
            create_background = self.route_backgrounds.create_route

            if create_background:
                for task in self.create_background:
                    background_tasks.add_task(task, db_model, request, current_user)

            return {"data": data}  # type: ignore

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self.pk_type,  # type: ignore
            model: self.update_schema,  # type: ignore
            request: Request,
            background_tasks: BackgroundTasks,
            db: AsyncSession = Depends(self.session),
            current_user: self.user_model = self.auth_info,
        ):
            sql = (
                update(self.db_model).filter_by(id=item_id).values(**model.model_dump())
            )
            try:
                await db.exec(sql)
                await db.commit()
            except IntegrityError as e:
                await db.rollback()
                self._raise(e)
            sql = select(self.db_model).where(self.db_model.id == item_id)
            result = await db.exec(sql)
            data = result.scalars().first().model_dump()
            update_background = self.route_backgrounds.update_route

            if update_background:
                for task in update_background:
                    background_tasks.add_task(task, data, request, current_user)
            return {"data": data}  # type: ignore

        return route

    def _tag_delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self.pk_type,  # type: ignore
            request: Request,
            background_tasks: BackgroundTasks,
            db: AsyncSession = Depends(self.session),
            current_user: self.user_model = self.auth_info,
        ):
            sql = update(self.db_model).filter_by(id=item_id).values(deleted=True)
            await db.exec(sql)
            await db.commit()
            sql = select(self.db_model).where(self.db_model.id == item_id)
            result = await db.exec(sql)
            data = result.scalars().first().model_dump()
            tag_delete_one_background = self.route_backgrounds.tag_delete_one_route

            if tag_delete_one_background:
                for task in tag_delete_one_background:
                    background_tasks.add_task(task, data, request, current_user)
            return {"data": data}  # type: ignore

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self.pk_type,  # type: ignore
            request: Request,
            background_tasks: BackgroundTasks,
            current_user: self.user_model = self.auth_info,
            db: AsyncSession = Depends(self.session),  # type: ignore
        ):
            sql = select(self.db_model).filter_by(id=item_id)
            result = await db.exec(sql)
            record = result.scalars().first()
            if not record:
                raise HTTPException(404, "Not found")
            statement = delete(self.db_model).filter_by(id=item_id)
            await db.exec(statement)
            await db.commit()
            delete_one_background = self.route_backgrounds.delete_one_route

            if delete_one_background:
                for task in delete_one_background:
                    background_tasks.add_task(
                        task, record.model_dump(), request, current_user
                    )
            return {"data": "success"}  # type: ignore

        return route

    def _count(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            filter_data: self.filter_model = None,
            db: AsyncSession = Depends(self.session),
        ):
            sql_generator = QuerySqlGenerator(
                model=self.schema,
                user_query_data=filter_data.model_dump() if filter_data else None,
                default_query_data=self.default_query_kwargs,
                user_sort_data={},
                default_sort_data={},
                filter_setting=self.filter_cfg,
            )
            sql_generator.generate_count_sql()
            sql = sql_generator.query_sql
            count = await db.exec(sql)
            count = count.one()
            return {"data": count}  # type: ignore

        return route

    def _change_status(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self.pk_type,  # type: ignore
            status: Literal[False, True],
            db: AsyncSession = Depends(self.session),
        ):
            sql = update(self.db_model).filter_by(id=item_id).values(disabled=status)
            await db.exec(sql)
            await db.commit()
            sql = select(self.db_model).where(self.db_model.id == item_id)
            result = await db.exec(sql)
            data = result.scalars().first().model_dump()
            return {"data": data}  # type: ignore

        return route

    def _export(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            path_name: str,
            filter_data: self.filter_model = None,
            db: AsyncSession = Depends(self.session),
        ):
            sql_generator = QuerySqlGenerator(
                model=self.schema,
                user_query_data=filter_data.model_dump() if filter_data else None,
                default_query_data=self.default_query_kwargs,
                user_sort_data={},
                default_sort_data={},
                filter_setting=self.filter_cfg,
            )
            sql_generator.generate_query_record_sql()
            sql = sql_generator.query_sql
            result = await db.exec(sql)
            data_list = [
                self.schema.model_validate(item).model_dump() for item in result.all()
            ]
            self.export_to_excel(path_name, data_list)
            return FileResponse(f"tmp/{path_name}.xlsx")  # type: ignore

        return route

    # 写一个函数，生成一个excel表格存储 data_list 列表
    def export_to_excel(self, path_name, data_list):
        """generate an excel file and store data_list in it.

        Args:
            data_list (_type_): _description_
        """
        webbook = Workbook("path_name.xlsx")
        sheet = webbook.active
        for row in data_list:
            sheet.append(row)
        webbook.save("path_name.xlsx")
