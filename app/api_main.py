from contextlib import asynccontextmanager

import uvicorn
from app.api.report_api import router
from fastapi import FastAPI

from app.initial_sample_data import initialize_sample_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_sample_data()
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, title="Test", version="0.1.0")
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.api_main:app", host="0.0.0.0", port=9000, reload=True)
