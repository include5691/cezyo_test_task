from fastapi import Depends
from sqlalchemy.orm import Session
from src.db.base import get_session
from src.repositories import PropertyRepository, ProductRepository

def get_property_repository(session: Session = Depends(get_session)) -> PropertyRepository:
    """
    Dependency to get a PropertyRepository instance with a database session.
    """
    return PropertyRepository(session)

def get_product_repository(session: Session = Depends(get_session)) -> ProductRepository:
    """
    Dependency to get a ProductRepository instance with a database session.
    """
    return ProductRepository(session)