from typing import ClassVar, Container, Type, List

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from pydantic import create_model
from pydantic.fields import FieldInfo, PydanticUndefined
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
import copy


class Choices(Enum):
    foo = "foo"
    bar = "bar"


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
    test: Choices = Field(default=Choices.foo)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email")
        return v

    @field_validator("account", mode="before")
    @classmethod
    def validate_account(cls, v):
        return hash_password(v)

from pydantic import validator, field_validator
def create_model_from_db_model(
    name_suffix: str,
    model: Type,
    is_update: bool = False,
    exclude: Container[str] = None,
    extra_field: List[dict] = None,
) -> Type[BaseModel]:
    """创建一个新model

    Args:
        db_model (Type): _description_
        is_update (bool, optional): _description_. Defaults to False.
        exclude (Container[str], optional): _description_. Defaults to None.
        extra_field (List[dict], optional): _description_. Defaults to None.

    Returns:
        Type[BaseModel]: _description_
    """
    if not extra_field:
        extra_field = {}
    old_fields = model.model_fields
    __validators__ = {}
    for k, v in old_fields.items():
        annotation = v.annotation
        if is_update:
            v.default = None
            v.nullable = False
        new_field = (annotation, v)
        if hasattr(model, f"validate_{k}"):
            f = getattr(model, f"validate_{k}").__func__
            validator_function = field_validator(k,mode="before")(f)
            __validators__[f"validate_{k}"] = validator_function

        extra_field[k] = new_field
    exclude = exclude or []
    for k in exclude:
        if k in extra_field.keys():
            del extra_field[k]
    pydantic_model = create_model(
        f"{model.__name__}{name_suffix}",
        __validators__=__validators__,
        **extra_field,
    )

    return pydantic_model


if __name__ == "__main__":
    extra_field = {
        "test": (
            str,
            FieldInfo(
                validator=None,
                alias=None,
                required=True,
                repr=True,
                default=PydanticUndefined,
            ),
        )
    }
    Company.model_validate = lambda self, data: None
    create_model_t = create_model_from_db_model(
        name_suffix="Create", model=Company, exclude=["id"], extra_field=extra_field
    )
    data = create_model_t(test="foo", name="bar", email="ssdcsd", account="23")
    print(data)
    create_model_t.model_validate(data)
