from typing import Dict, Type, TypeVar, Optional, Sequence, Union

from fastapi.params import Depends
from pydantic import BaseModel

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