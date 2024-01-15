

from api_model_manager.model_generator import create_model_from_db_model

from db_manager.db_models import Company


CompanyModelCreate = create_model_from_db_model(
    name_suffix="Create", model=Company, exclude=["id"]
)
CompanyModelupdate = create_model_from_db_model(
    name_suffix="Update", model=Company, exclude=["id"], is_update=True
)
