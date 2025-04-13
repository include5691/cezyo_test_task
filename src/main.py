import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from src.api.endpoints import property_router, products_router, catalog_router

app = FastAPI()

app.include_router(property_router)
app.include_router(products_router)
app.include_router(catalog_router)
