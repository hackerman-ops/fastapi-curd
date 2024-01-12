import traceback
from typing import Any, Callable, Dict, List, Type, Optional, Union
from annotated_types import T

from fastapi import BackgroundTasks
from fastapi import Depends, HTTPException
from fastapi import Request
from fastapi import Query
from fastapi_pagination import Params
from fastapi_pagination.bases import RawParams

from fastapi_pagination.ext.sqlalchemy import paginate as fastapi_paginate
from pydantic import BaseModel
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import DeclarativeMeta as Model
from sqlmodel import select, update, delete
from db_manager.engine import session
from ._base import CRUDGenerator, NOT_FOUND
from .curd_types import PYDANTIC_SCHEMA as SCHEMA
from .curd_types import DBSchemas, RouteBackgrounds, RouteDependencies
from ._utils import (
    QueryMaker,
    get_pk_type,
    create_filter_model_from_db_model_include_columns,
)

CALLABLE = Callable[..., Model]
CALLABLE_LIST = Callable[..., List[Model]]


def get_query_data(
    filter_cfg, db_model, filter_data, sorter_data, default_query_kwargs: dict = None
):
    """

    :param db_session:
    :param sort:
    :param filter_cfg:
    [
        {
            "key": "activation_platform_en",
            "condition": "==",
        },
        {
            "key": "activation_platform_cn",
            "condition": "contain",
        },
        {
            "key": "snapshot_date",
            "condition": "==",
        },
        {
            "key": "start_time",
            "condition": ">=",
            "real_name": "snapshot_date",
            "lbd": lambda v: timestamp_to_datetime(int(v / 1000))
        },
        {
            "key": "end_time",
            "condition": "<=",
            "real_name": "snapshot_date",
            "lbd": lambda v: timestamp_to_datetime(int(v / 1000))
        }
    ]
    :param db_model:
    :param filter_data:
    {
            "key1":"值1",
            "key2":"值2",
            "key3":"值3",
        }
    :param sorter_data:
        {
            "字段1":"ascend", //升序
            "字段2":"descend" //降序
        }
    :param pk:
    :return:
    """
    query = select(db_model)

    qm = QueryMaker(query)
    qm.add_filter(filter_data, db_model, default_query_kwargs)
    if filter_cfg:
        filter_keys = [filter["key"] for filter in filter_cfg]
        qm.filter_keys = filter_keys
        for filter in filter_cfg:
            qm.cfg_filter(
                key=filter.get("key"),
                condition=filter.get("condition"),
                model=filter.get("model", None),
                real_name=filter.get("real_name", None),
                lbd=filter.get("lbd", None),
            )
    qm.add_sorter(sorter_data, db_model)
    query = qm.get_query()
    return query


def get_query_count(
    filter_cfg, db_model, filter_data, default_query_kwargs: dict = None
):
    query = select(func.count("*")).select_from(db_model)

    qm = QueryMaker(query)
    qm.add_filter(filter_data, db_model, default_query_kwargs)
    if filter_cfg:
        filter_keys = [filter["key"] for filter in filter_cfg]
        qm.filter_keys = filter_keys
        for filter in filter_cfg:
            qm.cfg_filter(
                key=filter.get("key"),
                condition=filter.get("condition"),
                model=filter.get("model", None),
                real_name=filter.get("real_name", None),
                lbd=filter.get("lbd", None),
            )
    query = qm.get_query()
    return query


class SingleFilterCfg(BaseModel):
    key: str
    condition: str
    real_name: None
    lbd: Union[Callable, None]


class FilterCfg(BaseModel):
    filter_cfg: List[SingleFilterCfg] = []


class CustomParams(Params):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size,
            offset=self.size * (self.page - 1),
        )


class CRUDRouter(CRUDGenerator[SCHEMA]):
    def __init__(
        self,
        schemas: DBSchemas,
        db: session,
        route_dependencies: RouteDependencies,
        route_backgrounds: RouteBackgrounds,
        filter_cfg: List[SingleFilterCfg] = None,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        default_query_kwargs: Optional[dict] = None,
        default_sort_kwargs: Optional[dict] = None,
        check_create_duplicate: Optional[list] = None,
        current_user_pair: dict = None,
        **kwargs: Any
    ) -> None:
        self.user_model = current_user_pair.get("user_model")
        auth_info_func = current_user_pair.get("auth_info_func")
        self.auth_info = Depends(auth_info_func) if auth_info_func else Depends()

        db_model = schemas.db_schema
        self.db_model = db_model
        self.schema = db_model
        self.create_schema = schemas.create_schema
        self.update_schema = schemas.update_schema
        self.db_func = db
        self.route_backgrounds = route_backgrounds
        self.pk: str = db_model.__table__.primary_key.columns.keys()[0]
        self.pk_type: type = get_pk_type(db_model, self.pk)
        self.filter_cfg = filter_cfg
        self.filter_model = None
        if filter_cfg:
            mapping_list = []
            for co in filter_cfg:
                real_name = co.get("real_name")
                mapping = {
                    "new_key": co["key"],
                    "db_key": co["real_name"] if real_name else co["key"],
                }
                mapping_list.append(mapping)
            self.filter_model = create_filter_model_from_db_model_include_columns(
                name_suffix="create",
                model=self.schema,
                include=mapping_list,
                is_update=True,
            )
        self.default_query_kwargs = default_query_kwargs
        self.default_sort_kwargs = default_sort_kwargs
        self.check_create_duplicate = check_create_duplicate
        super().__init__(
            schemas=schemas,
            prefix=prefix or db_model.__tablename__,
            tags=tags,
            route_dependencies=route_dependencies,
            **kwargs
        )

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        def route(
            filter_data: self.filter_model = None,
            pagination: CustomParams = Depends(),
            sorter_data: Dict[str, str] = {},
            db: session = Depends(self.db_func),
        ) -> List[Model]:
            sorter_data.update(self.default_sort_kwargs)
            db_models: List[Model] = get_query_data(
                filter_cfg=self.filter_cfg,
                db_model=self.db_model,
                filter_data=filter_data,
                sorter_data=sorter_data,
                default_query_kwargs=self.default_query_kwargs,
            )
            page_data = fastapi_paginate(
                query=db_models,
                params=pagination,  # type: ignore
                conn=db,  # type: ignore
            )  # type: ignore
            data_list = [
                self.schema.model_validate(item).model_dump()
                for item in page_data.items
            ]
            page_data.items = data_list
            db.close()
            return {"data": page_data}  # type: ignore

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            item_id: self.pk_type, db: session = Depends(self.db_func)  # type: ignore
        ):
            sql = select(self.db_model).where(self.db_model.id == item_id)
            model = db.scalars(sql).first()
            if not model:
                raise NOT_FOUND
            data = model.model_dump()
            db.close()
            return {"data": data}  # type: ignore

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            model: self.create_schema,  # type: ignore
            request: Request,
            background_tasks: BackgroundTasks,
            db: session = Depends(self.db_func),
            current_user: self.user_model = self.auth_info,
        ):
            self.create_schema.model_validate(model)
            create_data = model.model_dump(exclude_unset=True, exclude_none=True)
            
            db_model = self.db_model(**create_data)
            print("======start=====")
            try:
                db.add(db_model)
                db.commit()
            except IntegrityError as e:
                traceback.print_exc()
                db.rollback()
                raise HTTPException(422, "Key already exists")
            print("======end=======")
            db.refresh(db_model)

            data = self.schema.model_validate(db_model).model_dump()

            # 创建后执行任务
            create_background = self.route_backgrounds.create_route

            if create_background:
                for task in self.create_background:
                    background_tasks.add_task(task, db_model, request, current_user)

            db.close()
            return {"data": data}  # type: ignore

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            item_id: self.pk_type,  # type: ignore
            model: self.update_schema,  # type: ignore
            request: Request,
            background_tasks: BackgroundTasks,
            db: session = Depends(self.db_func),
            current_user: self.user_model = self.auth_info,
        ):
            sql = (
                update(self.db_model).filter_by(id=item_id).values(**model.model_dump())
            )
            try:
                db.execute(sql)
                db.commit()
            except IntegrityError as e:
                db.rollback()
                self._raise(e)
            sql = select(self.db_model).where(self.db_model.id == item_id)
            data = db.scalars(sql).first().model_dump()
            update_background = self.route_backgrounds.update_route

            if update_background:
                for task in update_background:
                    background_tasks.add_task(task, data, request, current_user)
            db.close()
            return {"data": data}  # type: ignore

        return route

    def _tag_delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            item_id: self.pk_type,  # type: ignore
            request: Request,
            background_tasks: BackgroundTasks,
            db: session = Depends(self.db_func),
            current_user: self.user_model = self.auth_info,
        ):
            sql = update(self.db_model).filter_by(id=item_id).values(deleted=True)
            db.execute(sql)
            db.commit()
            sql = select(self.db_model).where(self.db_model.id == item_id)
            data = db.scalars(sql).first().model_dump()
            tag_delete_one_background = self.route_backgrounds.tag_delete_one_route

            if tag_delete_one_background:
                for task in tag_delete_one_background:
                    background_tasks.add_task(task, data, request, current_user)
            db.close()
            return {"data": data}  # type: ignore

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            item_id: self.pk_type,  # type: ignore
            request: Request,
            background_tasks: BackgroundTasks,
            current_user: self.user_model = self.auth_info,
            db: session = Depends(self.db_func),  # type: ignore
        ):
            sql = select(self.db_model).filter_by(id=item_id)
            record = db.scalars(sql).first()
            if not record:
                raise HTTPException(404, "Not found")
            statement = delete(self.db_model).filter_by(id=item_id)
            db.exec(statement)
            db.commit()
            delete_one_background = self.route_backgrounds.delete_one_route

            if delete_one_background:
                for task in delete_one_background:
                    background_tasks.add_task(
                        task, record.model_dump(), request, current_user
                    )
            db.close()
            return {"data": "success"}  # type: ignore

        return route

    def _count(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            filter_data: self.filter_model = None,
            db: session = Depends(self.db_func),
        ) -> List[Model]:
            db_models: List[Model] = get_query_count(
                filter_cfg=self.filter_cfg,
                db_model=self.db_model,
                filter_data=filter_data,
                default_query_kwargs=self.default_query_kwargs,
            )
            count = db.exec(db_models).one()

            db.close()
            return {"data": count}  # type: ignore

        return route

    def _change_status(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            item_id: self.pk_type,  # type: ignore
            status: bool,
            db: session = Depends(self.db_func),
        ):
            sql = update(self.db_model).filter_by(id=item_id).values(disabled=status)
            db.execute(sql)
            db.commit()
            sql = select(self.db_model).where(self.db_model.id == item_id)
            data = db.scalars(sql).first().model_dump()
            db.close()
            return {"data": data}  # type: ignore

        return route
