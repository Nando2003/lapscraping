from fastapi import FastAPI
from .laptop_scraping_route import router as laptop_router


def load_routes(app: FastAPI):
    app.include_router(laptop_router, prefix="/api")
    