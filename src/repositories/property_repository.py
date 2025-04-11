import uuid
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, delete, func, and_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from src.db.models import Property, PropertyListValue, ProductPropertyValue
from src.schemas.product import PropertyInputSchema, PropertyTypeEnum

class PropertyRepository:
    """
    Repository for handling database operations related to Properties and their list values.
    """
    def __init__(self, session: Session):
        self.db = session

    def get_by_uid(self, property_uid: uuid.UUID) -> Property | None:
        """
        Retrieves a property by its UID, optionally loading its list values if applicable.

        :param property_uid: The UUID of the property to retrieve.
        :return: The Property object or None if not found.
        """
        statement = select(Property).where(Property.uid == property_uid).options(
            selectinload(Property.values)
        )
        return self.db.execute(statement).scalar_one_or_none()

    def delete_property(self, property_uid: uuid.UUID):
        """
        Deletes a property, its associated list values, and any references
        in ProductPropertyValue.

        :param property_uid: The UUID of the property to delete.
        :return: True if the property was found and deleted, False otherwise.
        """
        db_property = self.get_by_uid(property_uid)
        if not db_property:
            return False

        delete_product_values_stmt = delete(ProductPropertyValue).where(
            ProductPropertyValue.property_uid == property_uid
        )
        self.db.execute(delete_product_values_stmt)
        self.db.delete(db_property)
        return True