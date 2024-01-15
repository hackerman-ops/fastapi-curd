from pydantic import BaseModel
from enum import Enum


class Choice(Enum):
    A = "A"
    B = "B"
    C = "F"


class Model(BaseModel):
    choice: Choice


# 测试代码
data = {"choice": "F"}
model = Model(**data)
print(model)
