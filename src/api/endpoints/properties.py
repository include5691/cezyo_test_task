from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.deps import PropertyRepository, get_property_repository, get_session
from src.schemas import PropertyInputSchema, PropertyOutputSchema

property_router = APIRouter(prefix="/properties", tags=["Properties"])


@property_router.post(
    "/", response_model=PropertyOutputSchema, status_code=status.HTTP_201_CREATED
)
async def create_property(
    property_data: PropertyInputSchema,
    session: Session = Depends(get_session),
    property_repo: PropertyRepository = Depends(get_property_repository),
):
    """
    Create a new property.
    """
    try:
        db_property = property_repo.create_property(property_data)
        session.commit()
        session.refresh(db_property)
        return db_property
    except ValueError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Property or Value UID already exists.",
        )


@property_router.delete("/{property_uid}", status_code=status.HTTP_200_OK)
async def delete_property(
    property_uid: UUID,
    session: Session = Depends(get_session),
    property_repo: PropertyRepository = Depends(get_property_repository),
):
    """
    Delete a property by its UID.
    """
    property_repo.delete_property(property_uid)
    session.commit()
    return {"message": "Property deleted successfully"}