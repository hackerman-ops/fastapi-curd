from typing import Dict, Type, TypeVar, Optional, Sequence, Union

from fastapi.params import Depends
from pydantic import BaseModel
from typing import Any, Callable, Dict, List, Type, Optional, Union
from annotated_types import T

from fastapi import Depends
from fastapi import Query
from fastapi_pagination import Params
from fastapi_pagination.bases import RawParams
from enum import Enum

from pydantic import BaseModel


class ResponseStruct(BaseModel):
    code: int = 200
    data: Any
    message: str = "success"


class Choices(Enum):
    e = "=="
    not_e = "!="
    lt = "<"
    lte = "<="
    gt = ">"
    gte = ">="
    in_ = "in"
    not_in = "~in"
    contain = "contain"


class FilterModel(BaseModel):
    key: str
    condition: Choices
    real_name: str = None
    lbd: Callable = None


PAGINATION = Dict[str, Optional[int]]
PYDANTIC_SCHEMA = BaseModel

T = TypeVar("T", bound=BaseModel)
DEPENDENCIES = Optional[Sequence[Depends]]


class DBSchemas(BaseModel):
    db_schema: Type[T]
    create_schema: Type[T] = None
    update_schema: Type[T] = None


class RouteDependencies(BaseModel):
    """dependencies list

    Args:
        BaseModel (_type_): _description_
    """

    common_dependencies: Union[bool, list] = True
    get_all_route: Union[bool, list] = True
    get_one_route: Union[bool, list] = True
    create_route: Union[bool, list] = True
    update_route: Union[bool, list] = True
    delete_one_route: Union[bool, list] = True
    tag_delete_one_route: Union[bool, list] = True
    count_route: Union[bool, list] = True
    change_status_route: Union[bool, list] = True
    export_route: Union[bool, list] = True


class RouteBackgrounds(BaseModel):
    """后台任务函数列表

    Args:
        BaseModel (_type_): _description_
    """

    get_all_route: Union[bool, list] = False
    get_one_route: Union[bool, list] = False
    create_route: Union[bool, list] = False
    update_route: Union[bool, list] = False
    delete_one_route: Union[bool, list] = False
    tag_delete_one_route: Union[bool, list] = False


class CustomParams(Params):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size,
            offset=self.size * (self.page - 1),
        )


class QueryAllParamsModel(BaseModel):
    filter_cfg: List[FilterModel] = (None,)
    default_query_kwargs: Optional[dict] = (None,)
    default_sort_kwargs: Optional[dict] = (None,)


class CurrentUserPair(BaseModel):
    user_model: Type[T]
    auth_info_func: Callable
