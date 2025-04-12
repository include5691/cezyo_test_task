import uuid
from sqlalchemy import Column, String, UUID, Enum
from sqlalchemy.orm import relationship
from src.db.base import Base

class Property(Base):
    __tablename__ = 'properties'

    uid = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    type = Column(Enum('int', 'list', name='property_type_enum'), nullable=False)
    product_assignments = relationship("ProductPropertyValue", back_populates="property")