from fastapi import FastAPI
from fastapi.routing import APIRoute
from src.pymodels.company_curd import company_router
from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from conf.base_model import ResponseStatusTypeCode
import logging
logger = logging.getLogger(__name__)


app = FastAPI()


app.include_router(company_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "type": ResponseStatusTypeCode().failed,
            "data": None,
            "code": exc.status_code,
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    args = exc.args
    error_columns = []
    for arg in args:
        for e in arg:
            loc = e["loc"][-1]
            error_columns.append(loc)

    description_list = {}
    annotation = request.scope["route"].body_field.field_info.annotation
    if hasattr(annotation, "model_fields"):
        model_fields = annotation.model_fields
        for k, v in model_fields.items():
            description_list[k] = v.description
            if hasattr(v.annotation, "model_fields"):
                second_model_fields = v.annotation.model_fields
                for k1, v1 in second_model_fields.items():
                    description_list[k1] = v1.description

    error_columns_chinese = [
        description_list[c] for c in error_columns if c in description_list.keys()
    ]

    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{exc_str}")
    content = {
        "message": "字段值输入错误, 请检查后重试",
        "type": ResponseStatusTypeCode().failed,
        "data": error_columns_chinese,
        "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
    }
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


