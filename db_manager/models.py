import re
from typing import Union

from pydantic import BaseModel, EmailStr
from sqlalchemy import Float
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine
from pydantic import field_validator
from sqlmodel.main import Undefined


class Company(SQLModel, table=True):
    __tablename__ = "company"
    id: Optional[int] = Field(default=Undefined, primary_key=True)
    name: str = Field(
        default=Undefined,
        unique=True,
        max_length=10,
        include=["1", "2"],
        description="公司名字",
    )
    email: str = Field(default=Undefined, unique=True)
    account: str = Field(default=Undefined, nullable=False, unique=True)
    number: int = Field(default=0, ge=0, le=100)

    @field_validator("email",mode="before")
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email")
        return v


class CompanyOrder(SQLModel, table=True):
    __tablename__ = "company_order"
    id: Optional[int] = Field(default=Undefined, primary_key=True)
    name: str = Field(default=Undefined, unique=True, max_length=10, include=["1", "2"])
    money: int = Field(Float, gt=0, lt=1000, nullable=False)

