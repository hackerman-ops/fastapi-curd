
import os


if os.getenv('DB_CURD_ROUTER_MODE') == 'async':
    from .async_curd_router import CRUDRouter
else:
    from .sync_curd_router import CRUDRouter