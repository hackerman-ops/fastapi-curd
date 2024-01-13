
from datetime  import datetime
from enum import Enum
import re
from typing import Union

from pydantic import BaseModel, EmailStr
from sqlalchemy import Float, text
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine
from pydantic import field_validator
from sqlmodel.main import Undefined
from api_model_manager.model_generator import create_model_from_db_model
import hashlib

from db_manager.db_models import Company




CompanyModelCreate = create_model_from_db_model(
    name_suffix="Create", model=Company, exclude=["id"]
)
CompanyModelupdate = create_model_from_db_model(
    name_suffix="Update", model=Company, exclude=["id"], is_update=True
)
