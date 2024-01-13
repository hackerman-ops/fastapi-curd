from pydantic import BaseModel
from fastapi_curd_router import async_curd_router
from db_manager.db_models import Company
from db_manager.async_engine import get_session
from fastapi_curd_router.curd_types import (
    DBSchemas,
    RouteBackgrounds,
    RouteDependencies,
)
from api_model_manager.api_models import CompanyModelCreate, CompanyModelupdate


from fastapi_curd_router.curd_types import FilterModel
from fastapi_curd_router.async_curd_router import QueryAllParamsModel
from fastapi_curd_router.async_curd_router import CurrentUserPair



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


company_router = async_curd_router.CRUDRouter(
    schemas=DBSchemas(
        db_schema=Company,
        create_schema=CompanyModelCreate,
        update_schema=CompanyModelupdate,
    ),
    route_backgrounds=RouteBackgrounds(),
    route_dependencies=RouteDependencies(common_dependencies=[]),
    tags=["company"],
    db=get_session,
    current_user_pair=CurrentUserPair(user_model=User, auth_info_func=get_current_user),
    query_params=QueryAllParamsModel(filter_cfg=filter_cfg),
)
