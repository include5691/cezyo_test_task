import uuid
from sqlalchemy import Column, String, UUID
from sqlalchemy.orm import relationship
from src.db.base import Base

class Product(Base):
    __tablename__ = 'products'

    uid = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True, index=True)
    property_values  = relationship("ProductPropertyValue", back_populates="product", cascade="all, delete-orphan", passive_deletes=True)