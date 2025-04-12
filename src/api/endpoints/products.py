from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.deps import get_product_repository, ProductRepository, get_session
from src.schemas import ProductOutputSchema

products_router = APIRouter(prefix="/product", tags=["Products"])


@products_router.get("/{uid}", response_model=ProductOutputSchema, status_code=status.HTTP_200_OK)
async def get_product(
    uid: UUID,
    product_repo: ProductRepository = Depends(get_product_repository),
):
    """
    Get a product.
    """
    product = product_repo.get_product(uid)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product