from fastapi import FastAPI
from fastapi.routing import APIRoute
from src.pymodels.async_company_curd import company_router


def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"


app = FastAPI()


app.include_router(company_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)


