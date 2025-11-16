from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from uuid import uuid4
from .base import Base


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(100), index=True)
    search_type = Column(String(20), nullable=False)  # image, text, url
    query_data = Column(JSONB, nullable=False)
    results_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<SearchHistory(id={self.id}, type='{self.search_type}', user_id='{self.user_id}')>"
