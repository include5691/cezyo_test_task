"""Add product, property, property list values and product proerty value models

Revision ID: 18ac5d5be3b3
Revises:
Create Date: 2025-04-11 02:18:35.620228

"""
from typing import Sequence, Union

import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '18ac5d5be3b3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# --- Define Table Structures for Data Insertion ---
products_table = sa.table('products',
    sa.column('uid', sa.UUID),
    sa.column('name', sa.String)
)

properties_table = sa.table('properties',
    sa.column('uid', sa.UUID),
    sa.column('name', sa.String),
    sa.column('type', sa.Enum('int', 'list', name='property_type_enum'))
)

property_list_values_table = sa.table('property_list_values',
    sa.column('value_uid', sa.UUID),
    sa.column('value', sa.String),
    sa.column('property_uid', sa.UUID)
)

product_property_values_table = sa.table('product_property_values',
    sa.column('id', sa.Integer), # Added ID column as it's in the table definition
    sa.column('product_uid', sa.UUID),
    sa.column('property_uid', sa.UUID),
    sa.column('int_value', sa.Integer),
    sa.column('list_value_uid', sa.UUID)
)

# --- Define Semantically Meaningful Test Data ---

# Properties
PROPERTIES_DATA = [
    # List properties
    {"uid": uuid.uuid4(), "name": "Color", "type": "list"},
    {"uid": uuid.uuid4(), "name": "Material", "type": "list"},
    {"uid": uuid.uuid4(), "name": "Operating System", "type": "list"},
    {"uid": uuid.uuid4(), "name": "Storage (GB)", "type": "list"},
    # Int properties
    {"uid": uuid.uuid4(), "name": "Screen Diagonal (inches)", "type": "int"},
    {"uid": uuid.uuid4(), "name": "Weight (kg)", "type": "int"}, # Using INT for simplicity, might be float in reality
    {"uid": uuid.uuid4(), "name": "Battery Capacity (mAh)", "type": "int"},
    {"uid": uuid.uuid4(), "name": "Release Year", "type": "int"},
]

# Map property names to their UIDs for easier lookup
property_uids = {prop['name']: prop['uid'] for prop in PROPERTIES_DATA}

# Property List Values
LIST_VALUES_DATA = [
    # Colors
    {"property_name": "Color", "value_uid": uuid.uuid4(), "value": "Black"},
    {"property_name": "Color", "value_uid": uuid.uuid4(), "value": "White"},
    {"property_name": "Color", "value_uid": uuid.uuid4(), "value": "Silver"},
    {"property_name": "Color", "value_uid": uuid.uuid4(), "value": "Blue"},
    {"property_name": "Color", "value_uid": uuid.uuid4(), "value": "Red"},
    {"property_name": "Color", "value_uid": uuid.uuid4(), "value": "Gray"}, # Added more colors
    {"property_name": "Color", "value_uid": uuid.uuid4(), "value": "Green"},
    # Materials
    {"property_name": "Material", "value_uid": uuid.uuid4(), "value": "Plastic"},
    {"property_name": "Material", "value_uid": uuid.uuid4(), "value": "Metal"},
    {"property_name": "Material", "value_uid": uuid.uuid4(), "value": "Glass"},
    {"property_name": "Material", "value_uid": uuid.uuid4(), "value": "Fabric"},
    {"property_name": "Material", "value_uid": uuid.uuid4(), "value": "Aluminum"}, # Added more materials
    {"property_name": "Material", "value_uid": uuid.uuid4(), "value": "Wood"},
    # OS
    {"property_name": "Operating System", "value_uid": uuid.uuid4(), "value": "Android"},
    {"property_name": "Operating System", "value_uid": uuid.uuid4(), "value": "iOS"},
    {"property_name": "Operating System", "value_uid": uuid.uuid4(), "value": "Windows"},
    {"property_name": "Operating System", "value_uid": uuid.uuid4(), "value": "MacOS"},
    {"property_name": "Operating System", "value_uid": uuid.uuid4(), "value": "WearOS"},
    {"property_name": "Operating System", "value_uid": uuid.uuid4(), "value": "Linux"}, # Added more OS
    {"property_name": "Operating System", "value_uid": uuid.uuid4(), "value": "Proprietary"}, # Generic OS
    # Storage
    {"property_name": "Storage (GB)", "value_uid": uuid.uuid4(), "value": "32"}, # Added smaller storage
    {"property_name": "Storage (GB)", "value_uid": uuid.uuid4(), "value": "64"},
    {"property_name": "Storage (GB)", "value_uid": uuid.uuid4(), "value": "128"},
    {"property_name": "Storage (GB)", "value_uid": uuid.uuid4(), "value": "256"},
    {"property_name": "Storage (GB)", "value_uid": uuid.uuid4(), "value": "512"},
    {"property_name": "Storage (GB)", "value_uid": uuid.uuid4(), "value": "1024"}, # 1TB
]

# Map list values to their UIDs for easier lookup (grouped by property name)
list_value_uids_by_prop = {}
for item in LIST_VALUES_DATA:
    prop_name = item["property_name"]
    if prop_name not in list_value_uids_by_prop:
        list_value_uids_by_prop[prop_name] = {}
    list_value_uids_by_prop[prop_name][item["value"]] = item["value_uid"]

# Products (Original 10 + 10 New)
PRODUCTS_DATA = [
    # --- Original 10 ---
    {"uid": uuid.uuid4(), "name": "Smartphone Alpha"},
    {"uid": uuid.uuid4(), "name": "Laptop Omega"},
    {"uid": uuid.uuid4(), "name": "Chair Comfort"},
    {"uid": uuid.uuid4(), "name": "Tablet TabX"},
    {"uid": uuid.uuid4(), "name": "Headphones SoundPro"},
    {"uid": uuid.uuid4(), "name": "Smartwatch WatchFit"},
    {"uid": uuid.uuid4(), "name": "TV VisionMax"},
    {"uid": uuid.uuid4(), "name": "Coffee Machine BrewExpert"},
    {"uid": uuid.uuid4(), "name": "Game Console PlayVerse"},
    {"uid": uuid.uuid4(), "name": "Camera ZoomMaster"},
    # --- New 10 ---
    {"uid": uuid.uuid4(), "name": "Desk Lamp BrightIdea"},
    {"uid": uuid.uuid4(), "name": "Router ConnectMax"},
    {"uid": uuid.uuid4(), "name": "Keyboard TypeFast"},
    {"uid": uuid.uuid4(), "name": "Mouse ClickPro"},
    {"uid": uuid.uuid4(), "name": "External SSD SpeedDisk"},
    {"uid": uuid.uuid4(), "name": "Backpack TravelLite"},
    {"uid": uuid.uuid4(), "name": "Blender MixMaster"},
    {"uid": uuid.uuid4(), "name": "E-Reader PageTurner"},
    {"uid": uuid.uuid4(), "name": "Projector ShowTime"},
    {"uid": uuid.uuid4(), "name": "Speaker SoundBlast"},
]

# Map product names to their UIDs
product_uids = {prod['name']: prod['uid'] for prod in PRODUCTS_DATA}

# Product Property Values (Links between products and property values)
PRODUCT_PROPERTY_VALUES_DATA = [
    # --- Original 10 Products ---
    # Smartphone Alpha
    {"product_name": "Smartphone Alpha", "property_name": "Color", "list_value": "Black"},
    {"product_name": "Smartphone Alpha", "property_name": "Material", "list_value": "Glass"},
    {"product_name": "Smartphone Alpha", "property_name": "Operating System", "list_value": "Android"},
    {"product_name": "Smartphone Alpha", "property_name": "Storage (GB)", "list_value": "128"},
    {"product_name": "Smartphone Alpha", "property_name": "Screen Diagonal (inches)", "int_value": 6},
    {"product_name": "Smartphone Alpha", "property_name": "Battery Capacity (mAh)", "int_value": 4500},
    {"product_name": "Smartphone Alpha", "property_name": "Release Year", "int_value": 2024},

    # Laptop Omega
    {"product_name": "Laptop Omega", "property_name": "Color", "list_value": "Silver"},
    {"product_name": "Laptop Omega", "property_name": "Material", "list_value": "Aluminum"}, # Changed to Aluminum
    {"product_name": "Laptop Omega", "property_name": "Operating System", "list_value": "Windows"},
    {"product_name": "Laptop Omega", "property_name": "Storage (GB)", "list_value": "512"},
    {"product_name": "Laptop Omega", "property_name": "Screen Diagonal (inches)", "int_value": 15},
    {"product_name": "Laptop Omega", "property_name": "Weight (kg)", "int_value": 2},
    {"product_name": "Laptop Omega", "property_name": "Release Year", "int_value": 2023},

    # Chair Comfort
    {"product_name": "Chair Comfort", "property_name": "Color", "list_value": "Blue"},
    {"product_name": "Chair Comfort", "property_name": "Material", "list_value": "Fabric"},
    {"product_name": "Chair Comfort", "property_name": "Weight (kg)", "int_value": 15},

    # Tablet TabX
    {"product_name": "Tablet TabX", "property_name": "Color", "list_value": "White"},
    {"product_name": "Tablet TabX", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "Tablet TabX", "property_name": "Operating System", "list_value": "Android"},
    {"product_name": "Tablet TabX", "property_name": "Storage (GB)", "list_value": "256"},
    {"product_name": "Tablet TabX", "property_name": "Screen Diagonal (inches)", "int_value": 10},
    {"product_name": "Tablet TabX", "property_name": "Battery Capacity (mAh)", "int_value": 7000},
    {"product_name": "Tablet TabX", "property_name": "Release Year", "int_value": 2023},

    # Headphones SoundPro
    {"product_name": "Headphones SoundPro", "property_name": "Color", "list_value": "Black"},
    {"product_name": "Headphones SoundPro", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "Headphones SoundPro", "property_name": "Weight (kg)", "int_value": 1}, # Using 1kg as approximation

    # Smartwatch WatchFit
    {"product_name": "Smartwatch WatchFit", "property_name": "Color", "list_value": "Red"},
    {"product_name": "Smartwatch WatchFit", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "Smartwatch WatchFit", "property_name": "Operating System", "list_value": "WearOS"},
    {"product_name": "Smartwatch WatchFit", "property_name": "Screen Diagonal (inches)", "int_value": 1},
    {"product_name": "Smartwatch WatchFit", "property_name": "Battery Capacity (mAh)", "int_value": 300},
    {"product_name": "Smartwatch WatchFit", "property_name": "Release Year", "int_value": 2024},

    # TV VisionMax
    {"product_name": "TV VisionMax", "property_name": "Color", "list_value": "Black"},
    {"product_name": "TV VisionMax", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "TV VisionMax", "property_name": "Screen Diagonal (inches)", "int_value": 55},
    {"product_name": "TV VisionMax", "property_name": "Release Year", "int_value": 2023},

     # Coffee Machine BrewExpert
    {"product_name": "Coffee Machine BrewExpert", "property_name": "Color", "list_value": "Silver"},
    {"product_name": "Coffee Machine BrewExpert", "property_name": "Material", "list_value": "Metal"},
    {"product_name": "Coffee Machine BrewExpert", "property_name": "Weight (kg)", "int_value": 5},

    # Game Console PlayVerse
    {"product_name": "Game Console PlayVerse", "property_name": "Color", "list_value": "White"},
    {"product_name": "Game Console PlayVerse", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "Game Console PlayVerse", "property_name": "Storage (GB)", "list_value": "1024"}, # 1TB
    {"product_name": "Game Console PlayVerse", "property_name": "Release Year", "int_value": 2022},

    # Camera ZoomMaster
    {"product_name": "Camera ZoomMaster", "property_name": "Color", "list_value": "Black"},
    {"product_name": "Camera ZoomMaster", "property_name": "Material", "list_value": "Metal"},
    {"product_name": "Camera ZoomMaster", "property_name": "Weight (kg)", "int_value": 1}, # Approx 0.6kg rounded
    {"product_name": "Camera ZoomMaster", "property_name": "Release Year", "int_value": 2021},

    # --- New 10 Products ---
    # Desk Lamp BrightIdea
    {"product_name": "Desk Lamp BrightIdea", "property_name": "Color", "list_value": "White"},
    {"product_name": "Desk Lamp BrightIdea", "property_name": "Material", "list_value": "Metal"},
    {"product_name": "Desk Lamp BrightIdea", "property_name": "Weight (kg)", "int_value": 1},

    # Router ConnectMax
    {"product_name": "Router ConnectMax", "property_name": "Color", "list_value": "Black"},
    {"product_name": "Router ConnectMax", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "Router ConnectMax", "property_name": "Weight (kg)", "int_value": 1}, # Approx 0.5kg rounded
    {"product_name": "Router ConnectMax", "property_name": "Release Year", "int_value": 2023},

    # Keyboard TypeFast
    {"product_name": "Keyboard TypeFast", "property_name": "Color", "list_value": "Gray"},
    {"product_name": "Keyboard TypeFast", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "Keyboard TypeFast", "property_name": "Weight (kg)", "int_value": 1},

    # Mouse ClickPro
    {"product_name": "Mouse ClickPro", "property_name": "Color", "list_value": "Black"},
    {"product_name": "Mouse ClickPro", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "Mouse ClickPro", "property_name": "Weight (kg)", "int_value": 1}, # Less than 1kg

    # External SSD SpeedDisk
    {"product_name": "External SSD SpeedDisk", "property_name": "Color", "list_value": "Silver"},
    {"product_name": "External SSD SpeedDisk", "property_name": "Material", "list_value": "Aluminum"},
    {"product_name": "External SSD SpeedDisk", "property_name": "Storage (GB)", "list_value": "1024"}, # 1TB
    {"product_name": "External SSD SpeedDisk", "property_name": "Weight (kg)", "int_value": 1}, # Less than 1kg

    # Backpack TravelLite
    {"product_name": "Backpack TravelLite", "property_name": "Color", "list_value": "Green"},
    {"product_name": "Backpack TravelLite", "property_name": "Material", "list_value": "Fabric"},
    {"product_name": "Backpack TravelLite", "property_name": "Weight (kg)", "int_value": 1},

    # Blender MixMaster
    {"product_name": "Blender MixMaster", "property_name": "Color", "list_value": "White"},
    {"product_name": "Blender MixMaster", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "Blender MixMaster", "property_name": "Weight (kg)", "int_value": 3},

    # E-Reader PageTurner
    {"product_name": "E-Reader PageTurner", "property_name": "Color", "list_value": "Black"},
    {"product_name": "E-Reader PageTurner", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "E-Reader PageTurner", "property_name": "Operating System", "list_value": "Proprietary"}, # Often Linux based, but proprietary UI
    {"product_name": "E-Reader PageTurner", "property_name": "Storage (GB)", "list_value": "32"},
    {"product_name": "E-Reader PageTurner", "property_name": "Screen Diagonal (inches)", "int_value": 6},
    {"product_name": "E-Reader PageTurner", "property_name": "Weight (kg)", "int_value": 1}, # Less than 1kg
    {"product_name": "E-Reader PageTurner", "property_name": "Battery Capacity (mAh)", "int_value": 1500},
    {"product_name": "E-Reader PageTurner", "property_name": "Release Year", "int_value": 2022},

    # Projector ShowTime
    {"product_name": "Projector ShowTime", "property_name": "Color", "list_value": "White"},
    {"product_name": "Projector ShowTime", "property_name": "Material", "list_value": "Plastic"},
    {"product_name": "Projector ShowTime", "property_name": "Weight (kg)", "int_value": 2},
    {"product_name": "Projector ShowTime", "property_name": "Release Year", "int_value": 2023},

    # Speaker SoundBlast
    {"product_name": "Speaker SoundBlast", "property_name": "Color", "list_value": "Blue"},
    {"product_name": "Speaker SoundBlast", "property_name": "Material", "list_value": "Fabric"},
    {"product_name": "Speaker SoundBlast", "property_name": "Weight (kg)", "int_value": 1},
    {"product_name": "Speaker SoundBlast", "property_name": "Battery Capacity (mAh)", "int_value": 5000},
]

def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###

    # Create Enum type explicitly for PostgreSQL if it doesn't exist
    op.create_table('products',
    sa.Column('uid', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)
    op.create_table('properties',
    sa.Column('uid', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('type', sa.Enum('int', 'list', name='property_type_enum'), nullable=False),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_table('property_list_values',
    sa.Column('value_uid', sa.UUID(), nullable=False),
    sa.Column('value', sa.String(length=255), nullable=False),
    sa.Column('property_uid', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['property_uid'], ['properties.uid'], ),
    sa.PrimaryKeyConstraint('value_uid')
    )
    op.create_table('product_property_values',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True), # Explicitly added autoincrement=True
    sa.Column('product_uid', sa.UUID(), nullable=False),
    sa.Column('property_uid', sa.UUID(), nullable=False),
    sa.Column('int_value', sa.Integer(), nullable=True),
    sa.Column('list_value_uid', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['list_value_uid'], ['property_list_values.value_uid'], ),
    sa.ForeignKeyConstraint(['product_uid'], ['products.uid'], ),
    sa.ForeignKeyConstraint(['property_uid'], ['properties.uid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_property_values_list_value_uid'), 'product_property_values', ['list_value_uid'], unique=False)
    op.create_index(op.f('ix_product_property_values_product_uid'), 'product_property_values', ['product_uid'], unique=False)
    op.create_index(op.f('ix_product_property_values_property_uid'), 'product_property_values', ['property_uid'], unique=False)
    # ### end Alembic commands ###

    # --- Begin Data Insertion ---
    # Make sure property UIDs are generated before inserting properties
    global property_uids
    property_uids = {prop['name']: prop['uid'] for prop in PROPERTIES_DATA}

    op.bulk_insert(
        properties_table,
        [
            {"uid": prop["uid"], "name": prop["name"], "type": prop["type"]}
            for prop in PROPERTIES_DATA
        ]
    )

    # Make sure list value UIDs are generated before inserting list values
    global list_value_uids_by_prop
    list_value_uids_by_prop = {}
    for item in LIST_VALUES_DATA:
        prop_name = item["property_name"]
        prop_uid = property_uids.get(prop_name) # Get UID using the fresh map
        if not prop_uid:
             print(f"Warning: Property '{prop_name}' not found for list value '{item['value']}'. Skipping.")
             continue # Skip if property doesn't exist
        if prop_name not in list_value_uids_by_prop:
            list_value_uids_by_prop[prop_name] = {}
        list_value_uids_by_prop[prop_name][item["value"]] = item["value_uid"]

    op.bulk_insert(
        property_list_values_table,
        [
            {
                "value_uid": item["value_uid"],
                "value": item["value"],
                "property_uid": property_uids[item["property_name"]], # Use fresh map
            }
            for item in LIST_VALUES_DATA if item["property_name"] in property_uids # Ensure property exists
        ]
    )

    # Make sure product UIDs are generated before inserting products
    global product_uids
    product_uids = {prod['name']: prod['uid'] for prod in PRODUCTS_DATA}

    op.bulk_insert(
        products_table,
        [
            {"uid": prod["uid"], "name": prod["name"]}
            for prod in PRODUCTS_DATA
        ]
    )

    # Prepare data for product_property_values, resolving UIDs
    product_property_values_to_insert = []
    for item in PRODUCT_PROPERTY_VALUES_DATA:
        prop_name = item["property_name"]
        prod_name = item["product_name"]
        prop_uid = property_uids.get(prop_name)
        prod_uid = product_uids.get(prod_name)

        if not prop_uid:
            print(f"Warning: Property '{prop_name}' not found for product '{prod_name}'. Skipping value.")
            continue
        if not prod_uid:
            print(f"Warning: Product '{prod_name}' not found. Skipping value.")
            continue

        int_val = item.get("int_value")
        list_val_str = item.get("list_value")
        list_val_uid = None

        if list_val_str:
            # Lookup the list value UID using the nested dictionary
            prop_values = list_value_uids_by_prop.get(prop_name, {})
            list_val_uid = prop_values.get(list_val_str)
            if not list_val_uid:
                print(f"Warning: List value '{list_val_str}' not found for property '{prop_name}' on product '{prod_name}'. Skipping value.")
                continue # Skip if list value doesn't exist for this property

        # Ensure either int_value or list_value_uid is present, not both
        if int_val is not None and list_val_uid is not None:
            print(f"Warning: Both int_value and list_value provided for property '{prop_name}' on product '{prod_name}'. Skipping value.")
            continue
        # Ensure at least one value is present (unless property allows null - not handled here)
        if int_val is None and list_val_uid is None:
             print(f"Warning: No value provided for property '{prop_name}' on product '{prod_name}'. Skipping value.")
             continue

        product_property_values_to_insert.append({
            "product_uid": prod_uid,
            "property_uid": prop_uid,
            "int_value": int_val,
            "list_value_uid": list_val_uid,
            # id is auto-generated, no need to specify here for bulk_insert
        })

    if product_property_values_to_insert: # Only insert if there's valid data
        op.bulk_insert(
            product_property_values_table,
            product_property_values_to_insert
        )


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_product_property_values_property_uid'), table_name='product_property_values')
    op.drop_index(op.f('ix_product_property_values_product_uid'), table_name='product_property_values')
    op.drop_index(op.f('ix_product_property_values_list_value_uid'), table_name='product_property_values')
    op.drop_table('product_property_values')
    op.drop_table('property_list_values')
    op.drop_table('properties')
    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.drop_table('products')

    # Drop Enum type explicitly for PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        property_type_enum_object = postgresql.ENUM('int', 'list', name='property_type_enum', create_type=False)
        property_type_enum_object.drop(bind, checkfirst=True)
    # ### end Alembic commands ###