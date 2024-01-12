from enum import Enum
from functools import cached_property
import random
import re
from typing import Literal, Union

from pydantic import BaseModel, EmailStr, computed_field
from sqlalchemy import Float
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine
from pydantic import field_validator
from sqlmodel.main import Undefined
from db_manager.model_generator import create_model_from_db_model


class Choices(Enum):
    foo = 'foo'
    bar = 'bar'

import hashlib

def hash_password(password: str) -> str:
    # 使用SHA-256算法对密码进行哈希
    return hashlib.sha256(password.encode()).hexdigest()

class Company(SQLModel, table=True):
    __tablename__ = "company"
    id: Optional[int] = Field(default=Undefined, primary_key=True)
    name: str = Field(
        default=Undefined,
        unique=True,
        max_length=10,
        description="公司名字",
    )
    email: str = Field(default=Undefined, unique=True)
    account: str = Field(default=Undefined, nullable=False, unique=True)
    number: int = Field(default=0, ge=0, le=100)
    # test: Choices = Field(default=Choices.foo)
    
    @field_validator("email",mode="before")
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email")
        return v
    
    @field_validator("account",mode="before")
    @classmethod
    def validate_account(cls,v):
        return hash_password(v)


class CompanyOrder(SQLModel, table=True):
    __tablename__ = "company_order"
    id: Optional[int] = Field(default=Undefined, primary_key=True)
    name: str = Field(default=Undefined, unique=True, max_length=10)
    money: int = Field(Float, gt=0, lt=1000, nullable=False)


CompanyModelCreate = create_model_from_db_model(
    name_suffix="Create", model=Company, exclude=["id"]
)
CompanyModelupdate = create_model_from_db_model(
    name_suffix="Update", model=Company, exclude=["id"], is_update=True
)
