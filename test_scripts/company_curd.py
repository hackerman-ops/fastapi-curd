from pydantic import BaseModel
from fastapi_curd_router import curd_router
from test_scripts.models import Company, CompanyModelCreate, CompanyModelupdate
from db_manager.engine import get_session
from fastapi_curd_router.curd_types import DBSchemas, RouteBackgrounds, RouteDependencies

class User(BaseModel):
    id: int
    name: str


def get_current_user():
    pass

filter_cfg = [
    {
        "key": "id",
        "condition": "eq",
    },
    {
        "key": "name",
        "condition": "like",
    },
        {
        "key": "new_name",
        "condition": "like",
        "real_name": "name"
    }
]


company_router = curd_router.CRUDRouter(
    schemas=DBSchemas(
        db_schema=Company,
        create_schema=CompanyModelCreate,
        update_schema=CompanyModelupdate,
    ),
    route_backgrounds=RouteBackgrounds(),
    route_dependencies=RouteDependencies(common_dependencies=[]),
    tags=["company"],
    db=get_session,
    current_user_pair={"user_model": User, "auth_info_func": get_current_user},
    filter_cfg=filter_cfg
)
