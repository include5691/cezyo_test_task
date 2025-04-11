import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI, status
from src.core.config import settings
from src.api.endpoints import property_router

app = FastAPI()

app.include_router(property_router)
