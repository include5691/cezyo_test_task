import uuid
from enum import StrEnum
from pydantic import BaseModel, Field, model_validator, model_serializer
from typing import List, Optional, Union

class PropertyTypeEnum(StrEnum):
    """Enum for the types of properties."""
    INT = "int"
    LIST = "list"

class PropertyOutputSchema(BaseModel):
    """Represents a single property associated with a product in the output."""
    uid: uuid.UUID = Field(..., description="Unique identifier of the property.", example="f47ac10b-58cc-4372-a567-0e02b2c3d479")
    name: str = Field(..., description="Name of the property.", example="Color")
    value_uid: Optional[uuid.UUID] = Field(None, description="Unique identifier of the selected value (for 'list' type properties).", example="a1b2c3d4-e5f6-7890-1234-567890abcdef")
    value: Optional[Union[int, str]] = Field(None, description="The actual value of the property (integer for 'int' type, string name for 'list' type).", example="Red")

    class Config:
        from_attributes = True

    @model_serializer
    def to_json(self) -> dict:
        base_json = {
            "uid": self.uid,
            "name": self.name,
        }
        if self.value_uid:
            base_json["value_uid"] = self.value_uid
        base_json["value"] = self.value
        return base_json

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

    @model_validator(mode="before")
    @classmethod
    def check_value(cls, data) -> dict:
        if data.get("type") == PropertyTypeEnum.LIST and not data.get("values"):
            raise ValueError("No values provided for property with type list")
        return data