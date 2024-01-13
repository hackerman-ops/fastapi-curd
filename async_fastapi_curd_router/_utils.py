import json
from typing import List, Optional, Type, Any

from fastapi import Depends, HTTPException
from pydantic import BaseModel, create_model

from .curd_types import T, PAGINATION, PYDANTIC_SCHEMA




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
            setattr(pydantic_model, f"validate_{new_key}", getattr(model, f"validate_{db_key}"))
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


class QueryMaker:
    """
    配合前端框架的数据结构，组装查询、排序条件
    """

    def __init__(self, queryset):
        self.queryset = queryset  # 初始的queryset

        """
        filter_cfg结构：
        {
            "字段名":{
                "value":字段值,
                "model":字段model,
                "condition":筛选条件, //等于:==,小于<,小于等于<=,大于>,大于等于>=,不等于!=,属于in,不属于~in,包含contain
                "real_name":真实字段名,
                "lambda":改变v的lambda
            }
        }

        sorter_cfg结构：
        {
            "字段名":{
                "condition":"ascend",
                "model":model,
                "real_name":真实字段名
            }
        }
        """
        self.filter_cfg = dict()  # 过滤参数
        self.sorter_cfg = dict()  # 排序参数
        self.filter_keys = []  # 合法的filter字段名，不在其中的会被过滤，为空则不校验

    def add_filter(self, filter_data, default_model, default_query_kwargs):
        """
        添加过滤参数，如果已有，则覆盖
        filter_data:{
            "key1":"值1",
            "key2":"值2",
            "key3":"值3",
        }
        default_model:默认的model
        """
        if filter_data:
            if isinstance(filter_data, str):
                filter_data = json.loads(filter_data)
        else:
            filter_data = {}
        if default_query_kwargs:
            filter_data.update(default_query_kwargs)
        for k, v in filter_data.items():
            # 过滤非法字段
            if self.filter_keys:
                if k not in self.filter_keys:
                    continue
            self.filter_cfg[k] = {
                "value": v,
                "model": default_model,
                "condition": "==",
                "real_name": k,
                "lambda": None,
            }

    def add_sorter(self, sorter_data, default_model):
        """
        添加排序参数
        sorter_data:{
            "字段1":"ascend", //升序
            "字段2":"descend" //降序
        }
        """
        if not sorter_data:
            return
        if isinstance(sorter_data, str):
            sorter_data = json.loads(sorter_data)

        for k, v in sorter_data.items():
            self.sorter_cfg[k] = {
                "condition": v,
                "model": default_model,
                "real_name": k,
            }

    def cfg_filter(self, key, condition=None, model=None, real_name=None, lbd=None):
        """
        特殊配置需要定制的查询条件，不能配置不存在的key
        """
        if condition is None and model is None and real_name is None and lbd is None:
            return

        if condition and condition not in [
            "==",
            "<",
            ">",
            "<=",
            ">=",
            "!=",
            "in",
            "~in",
            "contain",
        ]:
            return

        if key not in self.filter_cfg:
            return

        if condition:
            self.filter_cfg[key]["condition"] = condition

        if model:
            self.filter_cfg[key]["model"] = model

        if real_name:
            self.filter_cfg[key]["real_name"] = real_name

        if lbd:
            self.filter_cfg[key]["lambda"] = lbd

    def cfg_sorter(self, key, condition=None, model=None, real_name=None):
        """
        特殊配置需要定制的排序条件，不能配置不存在的key
        """
        if condition is None and model is None and real_name is None:
            return

        if condition and condition not in ["ascend", "descend"]:
            return

        if key not in self.sorter_cfg:
            return

        if condition:
            self.sorter_cfg[key]["condition"] = condition

        if model:
            self.sorter_cfg[key]["model"] = model

        if real_name:
            self.sorter_cfg[key]["real_name"] = real_name

    def get_query(self):
        """
        组装query
        """
        conditions = []
        for k, v in self.filter_cfg.items():
            model = v["model"]
            condition = v["condition"]
            value = v["value"]
            k = v["real_name"]
            if v["lambda"]:
                value = v["lambda"](value)
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
        query = self.queryset.where(*conditions)

        sort_conditions = []
        for k, v in self.sorter_cfg.items():
            model = v["model"]
            condition = v["condition"]
            k = v["real_name"]
            if condition == "ascend":
                sort_conditions.append(getattr(model, k).asc())
            else:
                sort_conditions.append(getattr(model, k).desc())
        query = query.order_by(*sort_conditions)

        return query
