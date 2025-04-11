from fastapi import Depends
from sqlalchemy.orm import Session
from src.db.base import get_session
from src.repositories import PropertyRepository

def get_property_repository(session: Session = Depends(get_session)) -> PropertyRepository:
    """
    Dependency to get a PropertyRepository instance with a database session.

    :return: An instance of PropertyRepository.
    """
    return PropertyRepository(session)