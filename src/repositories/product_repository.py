import uuid
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from src.db.models import (
    Product,
    ProductPropertyValue,
)
from src.schemas import PropertyTypeEnum, PropertyOutputSchema, ProductOutputSchema


class ProductRepository:
    """
    Repository for handling database operations related to Products and their properties.
    """

    def __init__(self, session: Session):
        self.db = session

    def get_product(self, product_uid: uuid.UUID):
        """
        Retrieves a product by its UID.
        """
        stmt = (
            select(Product)
            .where(Product.uid == product_uid)
            .options(
                selectinload(Product.property_values).options(
                    selectinload(ProductPropertyValue.list_value),
                    selectinload(ProductPropertyValue.property),
                )
            )
        )
        product_db = self.db.execute(stmt).scalar_one_or_none()
        if not product_db:
            return None
        product_properties_output = []
        for prop_value_db in product_db.property_values:
            property_db = prop_value_db.property
            list_value_db = prop_value_db.list_value
            prop_data = {
                "uid": property_db.uid,
                "name": property_db.name,
                "value_uid": None,
                "value": None,
            }
            if property_db.type == PropertyTypeEnum.INT:
                prop_data["value"] = prop_value_db.int_value
            elif property_db.type == PropertyTypeEnum.LIST and list_value_db:
                prop_data["value_uid"] = list_value_db.value_uid
                prop_data["value"] = list_value_db.value
            product_properties_output.append(PropertyOutputSchema(**prop_data))

        return ProductOutputSchema(
            uid=product_db.uid,
            name=product_db.name,
            properties=product_properties_output,
        )
