from sqlalchemy import Column, Integer, ForeignKey, UUID
from sqlalchemy.orm import relationship
from src.db.base import Base

class ProductPropertyValue(Base):
    __tablename__ = 'product_property_values'

    id = Column(Integer, primary_key=True)
    product_uid = Column(UUID, ForeignKey('products.uid', ondelete="CASCADE"), nullable=False, index=True)
    property_uid = Column(UUID, ForeignKey('properties.uid', ondelete="CASCADE"), nullable=False, index=True)
    int_value = Column(Integer)
    list_value_uid = Column(UUID, ForeignKey('property_list_values.value_uid', ondelete="CASCADE"), index=True)
    product = relationship("Product", back_populates="property_values")
    list_value = relationship("PropertyListValue", back_populates="product_assignments")
    property = relationship("Property", back_populates="product_assignments")