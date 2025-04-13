import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from src.db.models import Property, PropertyListValue
from src.schemas import PropertyTypeEnum, PropertyInputSchema

class PropertyRepository:
    """
    Repository for handling database operations related to Properties and their list values.
    """
    def __init__(self, session: Session):
        self.db = session

    def get_property_by_uid(self, property_uid: uuid.UUID) -> Property | None:
        """
        Retrieves a property by its UID
        """
        statement = select(Property).where(Property.uid == property_uid)
        return self.db.execute(statement).scalar_one_or_none()


    def create_property(self, property_data: PropertyInputSchema) -> Property:
        """
        Creates a new property in the database.
        Handles potential IntegrityErrors for duplicate UIDs.
        """
        if self.get_property_by_uid(property_data.uid):
            raise ValueError(f"Property with UID {property_data.uid} already exists.")
        if property_data.type == PropertyTypeEnum.LIST:
            value_exists_stmt = select(PropertyListValue.value_uid).where(
                PropertyListValue.value_uid.in_([uid.value_uid for uid in property_data.values]),
            )
            existing_value_uids = self.db.execute(value_exists_stmt).scalars().all()
            if existing_value_uids:
                raise ValueError(f"One or more values already exist: {existing_value_uids}")

        db_property = Property(
            uid=property_data.uid,
            name=property_data.name,
            type=property_data.type
        )

        if property_data.type == PropertyTypeEnum.LIST:
            for value_data in property_data.values:
                db_value = PropertyListValue(
                    value_uid=value_data.value_uid,
                    value=value_data.value
                )
                db_property.values.append(db_value)
        self.db.add(db_property)
        return db_property

    def delete_property(self, property_uid: uuid.UUID):
        """
        Deletes a property, its associated list values, and any references
        in ProductPropertyValue.
        """
        db_property = self.get_property_by_uid(property_uid)
        if not db_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found",
            )
        self.db.delete(db_property)