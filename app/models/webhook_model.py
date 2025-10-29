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
    def is_group(self) -> bool:
        """Return if the message is from a group"""
        jid = self.data.key.remoteJid or self.sender
        return "@g.us" in jid

    @property
    def is_me(self) -> Optional[str]:
        """Return if you were the one who sent the message"""
        return self.data.key.fromMe

    @property
    def user_message(self) -> Optional[str]:
        """Extract the text message"""
        msg = self.data.message
        if not msg:
            return None
        return msg.conversation

    @property
    def user_id(self) -> Optional[str]:
        """Extract only the phone number"""
        key = self.data.key
        jid = key.remoteJid or self.sender
        if not jid:
            return None
        return jid.split("@", 1)[0]
