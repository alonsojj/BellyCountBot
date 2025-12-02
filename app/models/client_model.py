from dataclasses import dataclass
from typing import Optional

from .enums import DocumentType, AccountingService


@dataclass
class Client:
    user_id: str
    name: Optional[str] = None
    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = None
    service: Optional[AccountingService] = None

    def to_dict(self):
        data = {
            "user_id": self.user_id,
            "name": self.name,
            "document_number": self.document_number,
        }
        if self.document_type:
            data["document_type"] = self.document_type.value
        if self.service:
            data["service"] = self.service.value
        return data
