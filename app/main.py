from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.domain.models
from app.domain.account import account_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("앱 시작")
    yield
    print("앱 종료")


app = FastAPI(lifespan=lifespan)


def include_routers(_app: FastAPI):
    _app.include_router(account_router.router)


include_routers(app)
