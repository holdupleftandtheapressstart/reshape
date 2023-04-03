from sqlalchemy import Column, String

from app.db import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(String, index=True, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    hash = Column(String, index=True, nullable=False)
    path = Column(String, nullable=False)
