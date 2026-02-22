from fastapi import FastAPI

import app.domain.models
from app.domain.account import account_router

app = FastAPI()


def include_routers(_app: FastAPI):
    _app.include_router(account_router.router)


include_routers(app)
