import uuid
from pydantic import BaseModel, Field
from typing import List, Optional
from .properties import PropertyOutputSchema

class ProductOutputSchema(BaseModel):
    """Represents a single product in the catalog list or detail view."""
    uid: uuid.UUID = Field(..., description="Unique identifier of the product.", example="c4a1b2d3-e4f5-6789-0123-456789abcdef")
    name: Optional[str] = Field(None, description="Name of the product.", example="Smartphone Model X")
    properties: List[PropertyOutputSchema] = Field(default_factory=list, description="List of properties associated with the product.")

    class Config:
        from_attributes = True

class CatalogOutputSchema(BaseModel):
    """Response schema for the catalog endpoint, containing products and total count."""
    products: List[ProductOutputSchema] = Field(..., description="List of products matching the query criteria for the current page.")
    count: int = Field(..., description="Total number of products matching the query criteria (across all pages).", example=50)


class PropertyValueInputSchema(BaseModel):
    """Schema for defining a property value when creating/updating a product."""
    uid: uuid.UUID = Field(..., description="UID of the property being assigned.", example="f47ac10b-58cc-4372-a567-0e02b2c3d479")
    value_uid: Optional[uuid.UUID] = Field(None, description="UID of the value selected from the property's list (required for 'list' type).", example="a1b2c3d4-e5f6-7890-1234-567890abcdef")
    value: Optional[int] = Field(None, description="Integer value for the property (required for 'int' type).", example=128)

class ProductInputSchema(BaseModel):
    """Schema for creating a new product."""
    uid: uuid.UUID = Field(..., description="Desired unique identifier for the new product.", example="c4a1b2d3-e4f5-6789-0123-456789abcdef")
    name: str = Field(..., description="Name of the new product.", example="Laptop Pro")
    properties: List[PropertyValueInputSchema] = Field(default_factory=list, description="List of property values to assign to the new product.")
