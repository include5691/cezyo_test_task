import uuid
from sqlalchemy import Column, String, UUID, Enum
from sqlalchemy.orm import relationship, Mapped
from src.db.base import Base
from .properties_list_values import PropertyListValue

class Property(Base):
    __tablename__ = 'properties'

    uid = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    type = Column(Enum('int', 'list', name='property_type_enum'), nullable=False)
    values: Mapped[list["PropertyListValue"]] = relationship('PropertyListValue', back_populates='property', cascade='all, delete-orphan', passive_deletes=True)