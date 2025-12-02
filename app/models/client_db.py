from sqlalchemy import Column, String, Enum
from app.db.base import Base
from app.models.enums import DocumentType


class ClientDB(Base):
    __tablename__ = "clients"

    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    document_type = Column(Enum(DocumentType), nullable=True)
    document_number = Column(String, nullable=True, unique=True)

    def __repr__(self):
        return f"<ClientDB(user_id='{self.user_id}', name='{self.name}')>"
