import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, exists
from src.db.models import (
    Product,
    ProductPropertyValue,
    Property,
    PropertyListValue
)
from src.schemas import PropertyTypeEnum, PropertyOutputSchema, ProductOutputSchema, ProductInputSchema


class ProductRepository:
    """
    Repository for handling database operations related to Products and their properties.
    """

    def __init__(self, session: Session):
        self.db = session

    def get_product(self, product_uid: uuid.UUID) -> ProductOutputSchema | None:
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

    def create_product(self, product_data: ProductInputSchema) -> ProductOutputSchema:
        """
        Creates a new product with specified properties after validation.
        Raises HTTPException if validation fails or UID conflict occurs.
        """
        if self.db.execute(select(exists().where(Product.uid == product_data.uid))).scalar():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with UID {product_data.uid} already exists.",
            )
        
        # create maps for existing properties and list values
        property_uids_input = {prop.uid for prop in product_data.properties}
        list_value_uids_input = {prop.value_uid for prop in product_data.properties if prop.value_uid}

        existing_properties_db = self.db.execute(
            select(Property).where(Property.uid.in_(property_uids_input))
        ).scalars().all()
        existing_properties_map = {prop.uid: prop for prop in existing_properties_db}

        existing_list_values_db = self.db.execute(
            select(PropertyListValue).where(PropertyListValue.value_uid.in_(list_value_uids_input))
        ).scalars().all()
        existing_list_values_map = {val.value_uid: val for val in existing_list_values_db}

        # validate properties
        validated_property_values = []
        for prop_input in product_data.properties:
            property_db = existing_properties_map.get(prop_input.uid)
            if not property_db:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Property with UID {prop_input.uid} does not exist.",
                )
            if property_db.type == PropertyTypeEnum.INT:
                if prop_input.value is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Integer value is required for property '{property_db.name}' (UID: {prop_input.uid}).",
                    )
                validated_property_values.append({
                    "property_uid": prop_input.uid,
                    "int_value": prop_input.value
                })

            elif property_db.type == PropertyTypeEnum.LIST:
                if prop_input.value_uid is None:
                     raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"value_uid is required for list property '{property_db.name}' (UID: {prop_input.uid}).",
                    )

                list_value_db = existing_list_values_map.get(prop_input.value_uid)
                if not list_value_db:
                     raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Property list value with value_uid {prop_input.value_uid} does not exist.",
                    )
                if list_value_db.property_uid != property_db.uid:
                     raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Property list value {prop_input.value_uid} does not belong to property {prop_input.uid}.",
                    )
                validated_property_values.append({
                    "property_uid": prop_input.uid,
                    "list_value_uid": prop_input.value_uid
                })
    
        # create product
        db_product = Product(
            uid=product_data.uid,
            name=product_data.name
        )
        self.db.add(db_product)

        # create property values
        for validated_value in validated_property_values:
            prop_value_db = ProductPropertyValue(
                product_uid=db_product.uid,
                property_uid=validated_value["property_uid"],
                int_value=validated_value.get("int_value"),
                list_value_uid=validated_value.get("list_value_uid")
            )
            self.db.add(prop_value_db)

        output_properties = []
        for prop_input in product_data.properties:
             property_db = existing_properties_map[prop_input.uid]
             prop_out_data = {
                 "uid": property_db.uid,
                 "name": property_db.name,
                 "value_uid": None,
                 "value": None
             }
             if property_db.type == PropertyTypeEnum.INT:
                 prop_out_data["value"] = prop_input.value
             elif property_db.type == PropertyTypeEnum.LIST:
                 list_value_db = existing_list_values_map[prop_input.value_uid]
                 prop_out_data["value_uid"] = prop_input.value_uid
                 prop_out_data["value"] = list_value_db.value
             output_properties.append(PropertyOutputSchema(**prop_out_data))

        return ProductOutputSchema(
            uid=product_data.uid,
            name=product_data.name,
            properties=output_properties
        )
    
    def delete_product(self, product_uid: uuid.UUID):
        """
        Deletes a product by its UID.
        """
        stmt = select(Product).where(Product.uid == product_uid)
        product_db = self.db.execute(stmt).scalar_one_or_none()
        if not product_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        self.db.delete(product_db)