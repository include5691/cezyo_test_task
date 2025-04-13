import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from starlette.requests import QueryParams
from sqlalchemy.orm import Session, aliased, selectinload, joinedload
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


def build_filtered_product_query(
    session: Session,
    name: Optional[str],
    query_params: Request.query_params
) -> select:
    """
    Builds the base SQLAlchemy query object containing products
    that match the name and property filters.
    Raises HTTPException for invalid filter combinations or non-existent properties.
    """
    base_query = select(Product)
    if name:
        base_query = base_query.where(Product.name.ilike(f"%{name}%"))

    property_filters = parse_property_filters(query_params)

    if property_filters:
        property_uids_to_check = list(property_filters)
        prop_types_stmt = select(Property.uid, Property.type).where(Property.uid.in_(property_uids_to_check))
        prop_type_results = session.execute(prop_types_stmt).all()
        prop_type_map = {uid: p_type for uid, p_type in prop_type_results}

        # Validate existence and filter types
        for prop_uid, filter_data in property_filters.items():
            if prop_uid not in prop_type_map:
                 raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Property with UID {prop_uid} used in filter does not exist.",
                 )
            prop_type = prop_type_map[prop_uid]
 
        # Apply filters using subqueries 
        for prop_uid, filter_data in property_filters.items():
            prop_type = prop_type_map.get(prop_uid)

            ppv_alias = aliased(ProductPropertyValue)
            subquery_conditions = [
                ppv_alias.product_uid == Product.uid,
                ppv_alias.property_uid == prop_uid
            ]
            if prop_type == PropertyTypeEnum.INT:
                has_int_filter = False
                if filter_data["int_from"] is not None:
                    subquery_conditions.append(ppv_alias.int_value >= filter_data["int_from"])
                    has_int_filter = True
                if filter_data["int_to"] is not None:
                    subquery_conditions.append(ppv_alias.int_value <= filter_data["int_to"])
                    has_int_filter = True
                if not has_int_filter: 
                    continue # Skip if _from/_to keys present but no valid values parsed
            elif prop_type == PropertyTypeEnum.LIST:
                 if filter_data["list_values"]:
                     subquery_conditions.append(ppv_alias.list_value_uid.in_(filter_data["list_values"]))
                 else:
                     continue # Skip if property_uid key present but no valid list values parsed

            exists_subquery = select(1).select_from(ppv_alias).where(and_(*subquery_conditions)).exists()
            base_query = base_query.where(exists_subquery)
    return base_query


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
    allowed_keys = {"page", "page_size", "name", "sort"}
    for key in request.query_params.keys():
        if not key.startswith("property_") and key not in allowed_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid query parameter '{key}'. Allowed parameters are 'page', 'page_size', 'name', 'sort', and 'property_*' filters.",
            )

    base_query = build_filtered_product_query(session, name, request.query_params)

    count_query = select(func.count()).select_from(base_query)
    total_count = session.execute(count_query).scalar_one()


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

    output_products = []
    for product_db in db_products:
        product_properties_output = []
        if product_db.property_values:
            for prop_value_db in product_db.property_values:
                product_properties_output.append(PropertyOutputSchema.from_db_models(property_db=prop_value_db.property, property_list_value_db=prop_value_db.list_value, product_property_value_db=prop_value_db))

        output_products.append(
            ProductOutputSchema(
                uid=product_db.uid,
                name=product_db.name,
                properties=product_properties_output,
            )
        )

    return CatalogOutputSchema(products=output_products, count=total_count)


@catalog_router.get("/filter/", response_model=Dict[str, Any])
async def get_catalog_filter(
    request: Request,
    session: Session = Depends(get_session),
    name: Optional[str] = Query(None, description="Substring search for product name (case-insensitive)."),
):
    """
    Returns filter statistics for products matching the query parameters.
    Provides total count and counts/ranges for relevant properties.
    """
    allowed_keys = {"name"}
    for key in request.query_params.keys():
        if not key.startswith("property_") and key not in allowed_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid query parameter '{key}' for filter endpoint. Allowed parameters are 'name' and 'property_*' filters.",
            )

    base_filtered_query = build_filtered_product_query(session, name, request.query_params)
    filtered_product_uids_subquery = base_filtered_query.with_only_columns(Product.uid).subquery()

    count_query = select(func.count()).select_from(filtered_product_uids_subquery)
    total_count = session.execute(count_query).scalar_one()

    filter_stats: Dict[str, Any] = {}

    # Stats for LIST properties
    list_stats_query = (
        select(
            ProductPropertyValue.property_uid,
            ProductPropertyValue.list_value_uid,
            func.count(func.distinct(ProductPropertyValue.product_uid)).label("value_count")
        )
        .join(filtered_product_uids_subquery, ProductPropertyValue.product_uid == filtered_product_uids_subquery.c.uid)
        .join(Property, ProductPropertyValue.property_uid == Property.uid)
        .where(Property.type == PropertyTypeEnum.LIST)
        .where(ProductPropertyValue.list_value_uid.is_not(None))
        .group_by(ProductPropertyValue.property_uid, ProductPropertyValue.list_value_uid)
    )
    list_stats_results = session.execute(list_stats_query).all()

    for row in list_stats_results:
        prop_uid_str = f"property_{row.property_uid}"
        if prop_uid_str not in filter_stats:
            filter_stats[prop_uid_str] = {}
        filter_stats[prop_uid_str][str(row.list_value_uid)] = row.value_count

    # Stats for INT properties
    int_stats_query = (
        select(
            ProductPropertyValue.property_uid,
            func.min(ProductPropertyValue.int_value).label("min_value"),
            func.max(ProductPropertyValue.int_value).label("max_value")
        )
        .join(filtered_product_uids_subquery, ProductPropertyValue.product_uid == filtered_product_uids_subquery.c.uid)
        .join(Property, ProductPropertyValue.property_uid == Property.uid)
        .where(Property.type == PropertyTypeEnum.INT)
        .where(ProductPropertyValue.int_value.is_not(None))
        .group_by(ProductPropertyValue.property_uid)
    )
    int_stats_results = session.execute(int_stats_query).all()

    for row in int_stats_results:
        if row.min_value is not None and row.max_value is not None:
            prop_uid_str = f"property_{row.property_uid}"
            filter_stats[prop_uid_str] = {
                "min_value": row.min_value,
                "max_value": row.max_value
            }

    response_data = {"count": total_count}
    response_data.update(filter_stats)

    return response_data