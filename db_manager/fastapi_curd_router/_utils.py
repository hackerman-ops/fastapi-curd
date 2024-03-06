from typing import List, Optional, Type, Any

from fastapi import Depends, HTTPException
from pydantic import BaseModel, create_model
from sqlalchemy.sql.expression import func
from .curd_types import T, PAGINATION, PYDANTIC_SCHEMA
from .curd_types import FilterModel
from sqlmodel import select
from sqlalchemy import Select


def create_filter_model_from_db_model_include_columns(
    name_suffix: str,
    model: Type,
    include: List[dict],
    is_update: bool = False,
) -> Type[BaseModel]:
    """创建一个新model

    Args:
        db_model (Type): _description_
        is_update (bool, optional): _description_. Defaults to False.
        exclude (Container[str], optional): _description_. Defaults to None.
        extra_field (List[dict], optional): _description_. Defaults to None.

    Returns:
        Type[BaseModel]: _description_
    """
    extra_field = {}
    old_fields = model.model_fields
    __validators__ = {}
    for k, v in old_fields.items():
        annotation = v.annotation
        if is_update:
            v.default = None
            v.nullable = False
        new_field = (annotation, v)
        extra_field[k] = new_field
    include = include or []
    new_fields = {}
    for k in include:
        new_key = k["new_key"]
        db_key = k["db_key"]
        new_fields[new_key] = extra_field[db_key]

    pydantic_model = create_model(
        f"{model.__name__}{name_suffix}",
        __base__=BaseModel,
        __validators__=__validators__,
        **new_fields,
    )  # type: ignore
    for k in include:
        new_key = k["new_key"]
        db_key = k["db_key"]
        if hasattr(model, f"validate_{db_key}"):
            setattr(
                pydantic_model,
                f"validate_{new_key}",
                getattr(model, f"validate_{db_key}"),
            )
    return pydantic_model


class AttrDict(dict):  # type: ignore
    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def get_pk_type(schema: Type[PYDANTIC_SCHEMA], pk_field: str) -> Any:
    try:
        return schema.__fields__[pk_field].annotation
    except KeyError:
        return int


def schema_factory(
    schema_cls: Type[T], pk_field_name: str = "id", name: str = "Create"
) -> Type[T]:
    """
    Is used to create a CreateSchema which does not contain pk
    """

    fields = {
        key: (f.annotation, ...)
        for key, f in schema_cls.__fields__.items()
        if key != pk_field_name
    }

    name = schema_cls.__name__ + name
    schema: Type[T] = create_model(__model_name=name, **fields)  # type: ignore
    return schema


def create_query_validation_exception(field: str, msg: str) -> HTTPException:
    return HTTPException(
        422,
        detail={
            "detail": [
                {"loc": ["query", field], "msg": msg, "type": "type_error.integer"}
            ]
        },
    )


def pagination_factory(max_limit: Optional[int] = None) -> Any:
    """
    Created the pagination dependency to be used in the router
    """

    def pagination(page: int = 0, size: Optional[int] = max_limit) -> PAGINATION:
        if page < 0:
            raise create_query_validation_exception(
                field="skip",
                msg="skip query parameter must be greater or equal to zero",
            )

        if size is not None:
            if size <= 0:
                raise create_query_validation_exception(
                    field="limit", msg="limit query parameter must be greater then zero"
                )

            elif max_limit and max_limit < size:
                raise create_query_validation_exception(
                    field="limit",
                    msg=f"limit query parameter must be less then {max_limit}",
                )

        return {"page": page, "size": size}

    return Depends(pagination)


class QuerySqlGenerator:
    def __init__(
        self,
        model,
        base_query: Select = None,
        user_query_data: dict = None,
        default_query_data: dict = None,
        filter_setting: list[FilterModel] = None,
        user_sort_data: dict = None,
        default_sort_data: dict = None,
    ) -> None:
        """生成sql

        Args:
            user_query_data (dict): 用户输入查询参数
            default_query_data (dict): 默认查询参数
            filter_setting (list): 代码限制查询字段
            user_sort_data (dict): 用户排序参数
            default_sort_data (dict): 默认排序参数
        """
        self.model = model
        self.base_query = base_query
        self.db_keys = model.model_fields.keys()
        # 有可能有非法字段，需要过滤
        # 输入字段和setting字段对比
        self.user_query_data = user_query_data or {}
        if default_query_data:
            self.user_query_data.update(default_query_data)

        # 有可能不是数据库字段，和数据库字段对比

        self.filter_setting = filter_setting or []

        # 和数据库字段对比
        self.user_sort_data = user_sort_data or {}
        if default_sort_data:
            self.user_sort_data.update(default_sort_data)
        self.legal_filter_setting = {}

        # 过滤掉不属于数据库字段的配置

        self.remove_illegal_filter_key()
        # 包含自定义key
        self.legal_filter_setting_keys = list(self.legal_filter_setting.keys())

    def remove_illegal_filter_key(self):
        """删除非法的查询参数"""
        # 过滤掉不属于数据库字段的配置
        for k in self.filter_setting:
            if k.key in self.db_keys and k.real_name == k.key:
                self.legal_filter_setting[k.key] = k
            if k.key not in self.db_keys and k.real_name in self.db_keys:
                self.legal_filter_setting[k.key] = k

    def remove_user_illegal_filter_key(self):
        """删除非法的查询参数"""
        for k in list(self.user_query_data.keys()):
            if k not in self.legal_filter_setting_keys:
                self.user_query_data.pop(k, True)

    def remove_user_illegal_sort_key(self):
        """删除非法的排序参数"""
        for k, v in self.user_sort_data.items():
            if k not in self.db_keys:
                self.user_sort_data.pop(k, True)
            if v not in ["asc", "desc"]:
                self.user_sort_data.pop(k, True)

    def get_base_query(self):
        """获取基础查询
        base query 有可能是连表查
        没有base query 就查单表
        """
        self.base_query = self.base_query if self.base_query else select(self.model)

    def generate_query_record_sql(self):
        """生成查询sql"""
        # 去掉不合法字段
        self.remove_user_illegal_filter_key()
        self.remove_user_illegal_sort_key()
        self.get_base_query()
        self.generate_filter_sql()
        self.generate_sort_sql()

    def generate_query_list_sql_with_no_sort(self):
        """生成查询sql"""
        # 去掉不合法字段
        self.remove_user_illegal_filter_key()
        self.remove_user_illegal_sort_key()
        self.get_base_query()
        self.generate_filter_sql()

    def generate_count_sql(self):
        self.remove_user_illegal_filter_key()
        self.base_query = select(func.count("*")).select_from(self.model)
        self.generate_filter_sql()

    def generate_filter_sql(self):
        """生成过滤条件sql"""

        conditions = []
        model = self.model
        for k, v in self.user_query_data.items():
            k_filter_setting: FilterModel = self.legal_filter_setting[k]

            condition = k_filter_setting.condition
            value = v
            if k_filter_setting.real_name:
                k = k_filter_setting.real_name
            if k_filter_setting.lbd:
                value = k_filter_setting.lbd(value)
            if condition == "==":
                conditions.append(getattr(model, k) == value)
            elif condition == "!=":
                conditions.append(getattr(model, k) != value)
            elif condition == "<":
                conditions.append(getattr(model, k) < value)
            elif condition == "<=":
                conditions.append(getattr(model, k) <= value)
            elif condition == ">":
                conditions.append(getattr(model, k) > value)
            elif condition == ">=":
                conditions.append(getattr(model, k) >= value)
            elif condition == "in":
                conditions.append(getattr(model, k).in_(value))
            elif condition == "~in":
                conditions.append(getattr(model, k).notin_(value))
            elif condition == "contain":
                conditions.append(getattr(model, k).contains(value))
        self.base_query = self.base_query.where(*conditions)

    def generate_sort_sql(self):
        """生成排序条件sql"""

        sort_conditions = []
        model = self.model
        for k, v in self.user_sort_data.items():
            condition = v
            if condition == "ascend":
                sort_conditions.append(getattr(model, k).asc())
            else:
                sort_conditions.append(getattr(model, k).desc())
        self.base_query = self.base_query.order_by(*sort_conditions)

    @property
    def query_sql(self):
        return self.base_query
