import uuid
from sqlalchemy import Column, String, UUID, ForeignKey
from src.db.base import Base

class PropertyListValue(Base):
    __tablename__ = 'property_list_values'

    value_uid = Column(UUID, primary_key=True, default=uuid.uuid4)
    value = Column(String(255), nullable=False)
    property_uid = Column(UUID, ForeignKey('properties.uid'), nullable=False)