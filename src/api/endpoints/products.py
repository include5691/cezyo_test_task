from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.deps import get_product_repository, ProductRepository, get_session
from src.schemas import ProductOutputSchema, ProductInputSchema

products_router = APIRouter(prefix="/product", tags=["Products"])


@products_router.get(
    "/{uid}", response_model=ProductOutputSchema, status_code=status.HTTP_200_OK
)
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


@products_router.post(
    "/", response_model=ProductOutputSchema, status_code=status.HTTP_201_CREATED
)
async def create_product(
    product: ProductInputSchema,
    product_repo: ProductRepository = Depends(get_product_repository),
    session: Session = Depends(get_session),
):
    """
    Create a new product.
    """
    product_db = product_repo.create_product(product)
    if not product_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product creation failed",
        )
    session.commit()
    return product_db

@products_router.delete(
    "/{uid}", status_code=status.HTTP_200_OK
)
async def delete_product(
    uid: UUID,
    product_repo: ProductRepository = Depends(get_product_repository),
    session: Session = Depends(get_session),
):
    """
    Delete a product.
    """
    product_repo.delete_product(uid)
    session.commit()
    return {"detail": "Product deleted successfully"}