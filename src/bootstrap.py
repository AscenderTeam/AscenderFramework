from ascender.common.api_docs import DefineAPIDocs
from ascender.core.database.provider import provideDatabase
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.core.router.provide import provideRouter
from ascender.core.types import IBootstrap
from routes import routes
from settings import DATABASE_CONNECTION


appBootstrap: IBootstrap = {
    "providers": [
        {
            "provide": DefineAPIDocs,
            "value": DefineAPIDocs(swagger_url="/docs", redoc_url="/redoc"),
        },
        provideRouter(routes),
        provideDatabase(ORMEnum.SQLALCHEMY, DATABASE_CONNECTION),
    ]
}
