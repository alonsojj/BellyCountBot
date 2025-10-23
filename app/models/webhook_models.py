from pydantic import BaseModel
from typing import Optional


class MessageKey(BaseModel):
    remoteJid: str
    fromMe: bool
    id: str
    participant: Optional[str] = ""


class Message(BaseModel):
    conversation: Optional[str] = None


class WebhookData(BaseModel):
    key: MessageKey
    pushName: Optional[str] = None
    message: Optional[Message] = None
    messageType: str
    messageTimestamp: int


class WebhookPayload(BaseModel):
    event: str
    instance: str
    data: WebhookData
    sender: str
    date_time: str

    @property
    def user_message(self) -> Optional[str]:
        """Extrai a mensagem de texto"""
        msg = self.data.message
        if not msg:
            return None
        return msg.conversation

    @property
    def user_name(self) -> str:
        """Retorna o nome do usuário"""
        return self.data.pushName or "Usuário"

    @property
    def number(self) -> Optional[str]:
        """Extrai o número do usuário (apenas dígitos)"""
        key = self.data.key
        jid = key.remoteJid or self.sender
        if not jid:
            return None
        return jid.split("@", 1)[0]
