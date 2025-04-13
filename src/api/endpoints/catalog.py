import uuid
from typing import List, Optional, Dict, Any, Tuple
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from starlette.requests import QueryParams
from sqlalchemy.orm import Session, aliased, selectinload, joinedload
from sqlalchemy.sql.expression import literal_column
from sqlalchemy import select, func, and_
from src.api.deps import get_session
from src.schemas import SortOptions, CatalogOutputSchema, ProductOutputSchema, PropertyOutputSchema, PropertyTypeEnum
from src.db.models import Product, ProductPropertyValue, Property

catalog_router = APIRouter(prefix="/catalog", tags=["Catalog"])


def parse_property_filters(query_params: QueryParams) -> Dict[str, Dict[str, Any]]:
    """
    Parses query parameters to extract property filters.
    Handles list values (property_uid=value1&property_uid=value2)
    and integer ranges (property_uid_from=X&property_uid_to=Y).
    """
    filters: Dict[str, Dict[str, Any]] = {} # uid: {list_values: [], int_from: None, int_to: None}
    for key in query_params.keys():
        if key.startswith("property_"):
            parts = key.split('_')
            prop_uid_str = parts[1]
            filter_type = parts[-1] if len(parts) > 2 else None # Check for _from or _to

            try:
                prop_uid = uuid.UUID(prop_uid_str)
            except ValueError:
                continue

            if prop_uid not in filters:
                filters[prop_uid] = {"list_values": [], "int_from": None, "int_to": None}

            values = query_params.getlist(key)
            if len(values) > 1:
                for value in values:
                    try:
                        filters[prop_uid]["list_values"].append(uuid.UUID(value))
                    except ValueError:
                        continue
                continue

            value = values[0]
            if filter_type == "from":
                try:
                    filters[prop_uid]["int_from"] = int(value)
                except (ValueError, TypeError):
                    continue
            elif filter_type == "to":
                 try:
                    filters[prop_uid]["int_to"] = int(value)
                 except (ValueError, TypeError):
                    continue
            else:
                try:
                    filters[prop_uid]["list_values"].append(uuid.UUID(value))
                except ValueError:
                        continue
    return {uid: data for uid, data in filters.items() if data["list_values"] or data["int_from"] is not None or data["int_to"] is not None}


@catalog_router.get("/", response_model=CatalogOutputSchema)
async def get_catalog(
    request: Request,
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1, description="Page number, starting from 1."),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page."),
    name: Optional[str] = Query(None, description="Substring search for product name (case-insensitive)."),
    sort: SortOptions = Query(SortOptions.UID, description="Sort order for products."),
):
    """
    Retrieves a paginated list of products with optional filtering and sorting.
    """
    # Check query keys
    if any(not key.startswith("property_") and key not in ["page", "page_size", "name", "sort"] for key in request.query_params.keys()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid query parameters. Please, use property_ prefix for property filters and only page, page_size, name, sort for other filters.",
        ) 

    # Create query
    base_query = select(Product)
    if name:
        base_query = base_query.where(Product.name.ilike(f"%{name}%"))
    property_filters = parse_property_filters(request.query_params)
    if property_filters:
        property_uids_to_check = list(property_filters)
        prop_types_stmt = select(Property.uid, Property.type).where(Property.uid.in_(property_uids_to_check))
        prop_type_results = session.execute(prop_types_stmt).all()
        prop_type_map = {uid: p_type for uid, p_type in prop_type_results}

        for prop_uid in property_uids_to_check:
            if prop_uid not in prop_type_map:
                 raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Property with UID {prop_uid} used in filter does not exist.",
                 )

        # Apply filters using subqueries
        for prop_uid, filter_data in property_filters.items():
            prop_type = prop_type_map.get(prop_uid)

            ppv_alias = aliased(ProductPropertyValue)
            subquery_filter = and_(
                ppv_alias.product_uid == Product.uid,
                ppv_alias.property_uid == prop_uid
            )

            if prop_type == PropertyTypeEnum.INT:
                int_conditions = []
                if filter_data["int_from"] is not None:
                    int_conditions.append(ppv_alias.int_value >= filter_data["int_from"])
                if filter_data["int_to"] is not None:
                    int_conditions.append(ppv_alias.int_value <= filter_data["int_to"])
                if filter_data["list_values"]:
                     raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot filter integer property {prop_uid} by list value UIDs.",
                    )
                subquery_filter = and_(subquery_filter, *int_conditions)

            elif prop_type == PropertyTypeEnum.LIST:
                 if filter_data["list_values"]:
                     subquery_filter = and_(
                         subquery_filter,
                         ppv_alias.list_value_uid.in_(filter_data["list_values"])
                     )
                 if filter_data["int_from"] is not None or filter_data["int_to"] is not None:
                      raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot filter list property {prop_uid} by integer range (_from/_to).",
                    )
            base_query = base_query.where(select(literal_column("1")).select_from(ppv_alias).where(subquery_filter).exists())

    # Apply pagination and sorting
    offset = (page - 1) * page_size
    query = base_query.options(
        selectinload(Product.property_values).options(
            joinedload(ProductPropertyValue.property),
            joinedload(ProductPropertyValue.list_value)
        )
    )
    if sort == SortOptions.NAME:
        query = query.order_by(Product.name)
    else:
        query = query.order_by(Product.uid)
    query = query.limit(page_size).offset(offset)
    db_products = session.execute(query).scalars().unique().all()

    # Format products for output
    output_products = []
    for product_db in db_products:
        product_properties_output = []
        if product_db.property_values:
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

        output_products.append(
            ProductOutputSchema(
                uid=product_db.uid,
                name=product_db.name,
                properties=product_properties_output,
            )
        )
    return CatalogOutputSchema(products=output_products, count=len(output_products))