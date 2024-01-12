from typing import Container, Type, List

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from pydantic import create_model
from pydantic.fields import PydanticUndefined
from pydantic import field_validator



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


