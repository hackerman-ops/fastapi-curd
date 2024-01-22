from pydantic import BaseModel
from db_manager.fastapi_curd_router.router_instance import CRUDRouter
from models.db_models import Company
from db_manager.fastapi_curd_router.curd_types import (
    DBSchemas,
    RouteBackgrounds,
    RouteDependencies,
)
from schemas.schemas import CompanyModelCreate, CompanyModelupdate

from db_manager.fastapi_curd_router.curd_types import FilterModel
from db_manager.fastapi_curd_router.curd_types import QueryAllParamsModel
from db_manager.fastapi_curd_router.curd_types import CurrentUserPair


class User(BaseModel):
    id: int
    name: str


def get_current_user():
    pass


filter_cfg = [
    FilterModel(key="id", condition="=="),
    FilterModel(key="account", condition="=="),
    FilterModel(key="new_name", condition="==", real_name="account"),
]


company_router = CRUDRouter(
    schemas=DBSchemas(
        db_schema=Company,
        create_schema=CompanyModelCreate,
        update_schema=CompanyModelupdate,
    ),
    route_backgrounds=RouteBackgrounds(),
    route_dependencies=RouteDependencies(common_dependencies=[]),
    tags=["company"],
    current_user_pair=CurrentUserPair(user_model=User, auth_info_func=get_current_user),
    query_params=QueryAllParamsModel(filter_cfg=filter_cfg),
)
