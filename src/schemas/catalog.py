from typing import List, Optional
from enum import StrEnum
from pydantic import BaseModel, Field
from .product import ProductOutputSchema


class SortOptions(StrEnum):
    """Enum for available sorting options for the catalog."""

    UID = "uid"
    NAME = "name"


class CatalogOutputSchema(BaseModel):
    """Response schema for the catalog endpoint, containing products and total count."""

    products: List[ProductOutputSchema] = Field(
        description="List of products matching the query criteria for the current page."
    )
    count: int = Field(
        ...,
        description="Total number of products matching the query criteria (across all pages).",
        example=20,
    )
