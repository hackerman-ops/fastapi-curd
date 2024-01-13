from sql_model.database import DBApi
from sql_model.models import ManageAccount


def store_update_account(db_model, request, current_user):
    store_id = db_model.id
    name_cn = db_model.name_cn

    api = DBApi()
    api.update_all(
        db_model=ManageAccount,
        condition={"store_id": store_id},
        update_info={"store_name": name_cn},
    )
