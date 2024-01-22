from datetime import datetime
from enum import Enum
import re

from sqlalchemy import Float, text
from sqlmodel import Field, SQLModel
from typing import Optional

from sqlmodel import Field, SQLModel
from pydantic import field_validator
from sqlmodel.main import Undefined
import hashlib


def hash_password(password: str) -> str:
    # 使用SHA-256算法对密码进行哈希
    return hashlib.sha256(password.encode()).hexdigest()


class Choices(Enum):
    foo = "foo"
    bar = "bar"


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
    test: Choices = Field(default=Choices.foo.value, nullable=False)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email")
        return v

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp(0)")},
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"),
            "onupdate": text("current_timestamp(0)"),
        },
    )

    @field_validator("account", mode="before")
    @classmethod
    def validate_account(cls, v):
        return hash_password(v)

    __table_args__ = {"extend_existing": True}


class CompanyOrder(SQLModel, table=True):
    __tablename__ = "company_order"
    id: Optional[int] = Field(default=Undefined, primary_key=True)
    name: str = Field(default=Undefined, unique=True, max_length=10)
    money: int = Field(Float, gt=0, lt=1000, nullable=False)
