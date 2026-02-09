from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Test", version="0.1.0")
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.api_main:app", host="0.0.0.0", port=9000, reload=True)