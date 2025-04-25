from fastapi import FastAPI
from app.routes import router
from app.db import init

app = FastAPI()

app.include_router(router)

@app.on_event("startup")
async def startup():
    await init()
