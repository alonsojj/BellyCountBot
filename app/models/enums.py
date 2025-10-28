from enum import Enum, auto


class ConversationState(Enum):
    GREETING = auto()
    AWAITING_DETAIL = auto()
    SERVICE_SELECTION = auto()
    AWAITING_SPECIFIC_DETAIL = auto()
    COMPLETED = auto()
    DOUBTS = auto()


class AccountingService(Enum):
    INCOME_TAX = auto()


class DocumentType(Enum):
    CPF = "CPF"
    CNPJ = "CNPJ"
