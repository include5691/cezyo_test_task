from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.deps import PropertyRepository, get_property_repository, get_session

property_router = APIRouter(prefix="/properties", tags=["Properties"])


@property_router.delete("/{property_uid}", status_code=status.HTTP_200_OK)
async def delete_property(
    property_uid: UUID,
    session: Session = Depends(get_session),
    property_repo: PropertyRepository = Depends(get_property_repository),
):
    """
    Delete a property by its UID.

    :param property_uid: The UUID of the property to delete.
    :param property_repo: The PropertyRepository instance.
    :raises HTTPException: If the property is not found or if it cannot be deleted.
    """
    if not property_repo.delete_property(property_uid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    session.commit()
    return {"message": "Property deleted successfully"}
