from fastapi import FastAPI
from .api import webhook
from .api import admin
import asyncio
import logging
from app.core.dependencies import get_chatbot_service, get_whatsapp_service

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="BellyCountBot")

app.include_router(webhook.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


INACTIVITY_CHECK_INTERVAL = 30
INACTIVITY_MINUTES = 1

inactivity_checker_task = None


async def inactivity_checker():
    """
    Background task to periodically check for inactive user sessions and clean them up.
    """
    chatbot_service = get_chatbot_service()
    whatsapp_service = get_whatsapp_service()

    while True:
        try:
            inactive_user_ids = chatbot_service.check_inactivity_and_cleanup(
                INACTIVITY_MINUTES
            )
            for session in inactive_user_ids:
                logging.info(
                    f"Sessão do usuário {session.client.user_id} inativa por {INACTIVITY_MINUTES} minutos. Enviando mensagem de encerramento."
                )
                whatsapp_service.send_text(
                    session.client.user_id,
                    "Olá! Parece que você ficou ausente por um tempo. Para recomeçar, por favor, envie uma nova mensagem.",
                    session.whatsapp_instance,
                )
                chatbot_service.delete_session(session.client.user_id)
                logging.info(
                    f"Sessão do usuário {session.client.user_id} encerrada devido à inatividade."
                )
        except Exception as e:
            logging.error(f"Erro no verificador de inatividade: {e}")

        await asyncio.sleep(INACTIVITY_CHECK_INTERVAL)
