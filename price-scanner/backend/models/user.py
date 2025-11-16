from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(200))
    subscription_tier = Column(String(20), default="free")  # free, pro, enterprise
    api_key = Column(String(100), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', tier='{self.subscription_tier}')>"


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    target_price = Column(DECIMAL(10, 2))
    notify_on_price_drop = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="watchlists")
    product = relationship("Product", back_populates="watchlists")

    def __repr__(self):
        return f"<Watchlist(user_id={self.user_id}, product_id={self.product_id})>"
