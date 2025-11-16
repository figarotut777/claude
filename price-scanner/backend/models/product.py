from sqlalchemy import Column, String, Text, DECIMAL, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from .base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    image_url = Column(String(1000))
    category = Column(String(200))
    brand = Column(String(200))
    normalized_name = Column(String(500), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    listings = relationship("MarketplaceListing", back_populates="product", cascade="all, delete-orphan")
    watchlists = relationship("Watchlist", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    marketplace = Column(String(50), nullable=False, index=True)
    marketplace_product_id = Column(String(200))
    url = Column(String(1000), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False, index=True)
    currency = Column(String(3), default="USD")
    rating = Column(DECIMAL(3, 2))
    reviews_count = Column(Integer)
    in_stock = Column(Boolean, default=True)
    seller_name = Column(String(200))
    shipping_cost = Column(DECIMAL(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="listings")
    price_history = relationship("PriceHistory", back_populates="listing", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MarketplaceListing(id={self.id}, marketplace='{self.marketplace}', price={self.price})>"


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("marketplace_listings.id", ondelete="CASCADE"))
    price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    listing = relationship("MarketplaceListing", back_populates="price_history")

    def __repr__(self):
        return f"<PriceHistory(listing_id={self.listing_id}, price={self.price}, recorded_at={self.recorded_at})>"
