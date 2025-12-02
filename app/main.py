from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import logging

from .api import webhook, admin
from app.db.base import Base, engine
from app.core.dependencies import get_chatbot_service, get_whatsapp_service

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Lógica de Tarefas e Configuração ---

INACTIVITY_CHECK_INTERVAL = 30
INACTIVITY_MINUTES = 1


def create_db_and_tables():
    logging.info("Criando/Verificando tabelas do banco de dados...")
    Base.metadata.create_all(bind=engine)
    logging.info("Tabelas do banco de dados prontas.")


async def inactivity_checker():
    """
    Background task to periodically check for inactive user sessions and clean them up.
    """
    logging.info("Iniciando verificador de inatividade de sessão.")
    chatbot_service = get_chatbot_service()
    whatsapp_service = get_whatsapp_service()

    while True:
        await asyncio.sleep(INACTIVITY_CHECK_INTERVAL)
        try:
            inactive_user_ids = chatbot_service.check_inactivity_and_cleanup(
                INACTIVITY_MINUTES
            )
            for session in inactive_user_ids:
                logging.info(
                    f"Sessão do usuário {session.client.user_id} inativa. Encerrando."
                )
                whatsapp_service.send_text(
                    session.client.user_id,
                    "Olá! Parece que você ficou ausente por um tempo. Para recomeçar, por favor, envie uma nova mensagem.",
                    session.whatsapp_instance,
                )
                chatbot_service.delete_session(session.client.user_id)
        except Exception as e:
            logging.error(f"Erro no verificador de inatividade: {e}")


# --- Gerenciador de Ciclo de Vida (Lifespan) ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    inactivity_task = asyncio.create_task(inactivity_checker())

    yield

    logging.info("Encerrando aplicação. Cancelando tarefas em segundo plano.")
    inactivity_task.cancel()
    try:
        await inactivity_task
    except asyncio.CancelledError:
        logging.info("Tarefa de inatividade cancelada com sucesso.")


app = FastAPI(title="BellyCountBot", lifespan=lifespan)

app.include_router(webhook.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
