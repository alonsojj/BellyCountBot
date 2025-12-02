from sqlalchemy import Column, String, Enum
from app.db.base import Base
from app.models.enums import DocumentType


class ClientDB(Base):
    __tablename__ = "clients"

    document_number = Column(
        String, primary_key=True, index=True, unique=True, nullable=False
    )
    document_type = Column(Enum(DocumentType), nullable=True)
    name = Column(String, nullable=True)
    phone = Column(String, index=True)

    def __repr__(self):
        return (
            f"<ClientDB(document_number='{self.document_number}', name='{self.name}')>"
        )
