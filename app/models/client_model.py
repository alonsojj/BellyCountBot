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
