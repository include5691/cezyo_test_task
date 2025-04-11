import uuid
from enum import StrEnum
from pydantic import BaseModel, Field
from typing import List, Optional, Union

__all__ = ["ProductPropertyOutputSchema", "ProductOutputSchema", "CatalogOutputSchema", "PropertyValueInputSchema", "ProductInputSchema", "PropertyListValueInputSchema", "PropertyInputSchema", "PropertyTypeEnum", "SortOptions"]

class PropertyTypeEnum(StrEnum):
    """Enum for the types of properties."""
    INT = "int"
    LIST = "list"

class SortOptions(StrEnum):
    """Enum for available sorting options for the catalog."""
    UID = "uid"
    NAME = "name"

# Output Schemas

class ProductPropertyOutputSchema(BaseModel):
    """Represents a single property associated with a product in the output."""
    uid: uuid.UUID = Field(..., description="Unique identifier of the property.", example="f47ac10b-58cc-4372-a567-0e02b2c3d479")
    name: str = Field(..., description="Name of the property.", example="Color")
    value_uid: Optional[uuid.UUID] = Field(None, description="Unique identifier of the selected value (for 'list' type properties).", example="a1b2c3d4-e5f6-7890-1234-567890abcdef")
    value: Optional[Union[int, str]] = Field(None, description="The actual value of the property (integer for 'int' type, string name for 'list' type).", example="Red")

    class Config:
        from_attributes = True

class ProductOutputSchema(BaseModel):
    """Represents a single product in the catalog list or detail view."""
    uid: uuid.UUID = Field(..., description="Unique identifier of the product.", example="c4a1b2d3-e4f5-6789-0123-456789abcdef")
    name: Optional[str] = Field(None, description="Name of the product.", example="Smartphone Model X")
    properties: List[ProductPropertyOutputSchema] = Field(default_factory=list, description="List of properties associated with the product.")

    class Config:
        from_attributes = True

class CatalogOutputSchema(BaseModel):
    """Response schema for the catalog endpoint, containing products and total count."""
    products: List[ProductOutputSchema] = Field(..., description="List of products matching the query criteria for the current page.")
    count: int = Field(..., description="Total number of products matching the query criteria (across all pages).", example=50)

# Input Schemas

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

class PropertyListValueInputSchema(BaseModel):
    """Schema for defining a single possible value within a 'list' type property."""
    value_uid: uuid.UUID = Field(..., description="Unique identifier for this specific value option.", example="a1b2c3d4-e5f6-7890-1234-567890abcdef")
    value: str = Field(..., description="The display string for this value option.", example="256GB")

class PropertyInputSchema(BaseModel):
    """Schema for creating a new property."""
    uid: uuid.UUID = Field(..., description="Desired unique identifier for the new property.", example="f47ac10b-58cc-4372-a567-0e02b2c3d479")
    name: str = Field(..., description="Name of the new property.", example="Storage Capacity")
    type: PropertyTypeEnum = Field(..., description="Type of the property ('int' or 'list').", example=PropertyTypeEnum.LIST)
    values: Optional[List[PropertyListValueInputSchema]] = Field(None, description="List of possible values (required and only used if type is 'list').")