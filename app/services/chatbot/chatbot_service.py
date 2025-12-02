import logging
from datetime import datetime
from typing import Optional

# Importações de DB
from app.db.base import SessionLocal
from app.services.db_service import get_client, create_or_update_client
from app.models.client_model import Client

from app.models.enums import ConversationState, AccountingService
from app.models.user_session import UserSession
from app.services.ia_service import IaService
from app.services.document_service import (
    consultar_cnpj_empresa,
    CNPJData,
)
from app.services.email_service import EmailService

from .handlers.greeting import GreetingHandler
from .handlers.initial_option import InitialOptionHandler
from .handlers.cpf_cnpj import CpfCnpjHandler
from .handlers.pf_name import PfNameHandler
from .handlers.pf_service_choice import PfServiceChoiceHandler
from .handlers.pj_service_choice import PjServiceChoiceHandler
from .handlers.dept_pessoal_question1 import DeptPessoalQuestion1Handler
from .handlers.abertura_empresa_question1 import AberturaEmpresaQuestion1Handler
from .handlers.planejamento_menu import PlanejamentoMenuHandler
from .handlers.ia_confirmation import IaConfirmationHandler
from .handlers.doubts import DoubtsHandler
from .handlers.human_attendance import HumanAttendanceHandler
from .handlers.ia_classify_await_description import IaClassifyAwaitDescriptionHandler


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ChatbotService:
    """
    Orquestrador principal do chatbot. Gerencia sessões e direciona as mensagens
    para o handler de estado apropriado.
    """

    def __init__(self, ia: IaService, email_service: EmailService):
        self.user_sessions = {}
        self.ia = ia
        self.email_service = email_service
        logging.info("ChatbotService iniciado")

        self.state_handlers = {
            ConversationState.GREETING: GreetingHandler(),
            ConversationState.AGUARDANDO_OPCAO_INICIAL: InitialOptionHandler(),
            ConversationState.AGUARDANDO_CPF_CNPJ: CpfCnpjHandler(),
            ConversationState.AGUARDANDO_NOME_PF: PfNameHandler(),
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF: PfServiceChoiceHandler(),
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ: PjServiceChoiceHandler(),
            ConversationState.SERVICO_DEPTO_PESSOAL_PERGUNTA_1: DeptPessoalQuestion1Handler(),
            ConversationState.SERVICO_ABERTURA_EMPRESA_PERGUNTA_1: AberturaEmpresaQuestion1Handler(),
            ConversationState.SERVICO_PLANEJAMENTO_MENU: PlanejamentoMenuHandler(),
            ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION: IaClassifyAwaitDescriptionHandler(),
            ConversationState.SERVICO_IA_CLASSIFY_AWAIT_CONFIRMATION: IaConfirmationHandler(),
            ConversationState.DOUBTS: DoubtsHandler(),
            ConversationState.ATENDIMENTO_HUMANO: HumanAttendanceHandler(),
            ConversationState.HUMAN_ATTENDING: HumanAttendanceHandler(),
        }

    def _get_session(
        self, user_id: str, whatsapp_instance: Optional[str] = None
    ) -> UserSession:
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = UserSession(user_id)
            logging.info(f"Nova sessão criada para o usuário: {user_id}")
        return self.user_sessions[user_id]

    def get_session_state(self, user_id: str) -> ConversationState:
        session = self._get_session(user_id)
        return session.state

    def _set_state(self, session: UserSession, new_state: ConversationState):
        if session.state != new_state:
            session.previous_state = session.state
        session.state = new_state

    async def process_message(
        self, user_id: str, user_message: str, whatsapp_instance: Optional[str] = None
    ) -> str:
        session = self._get_session(user_id, whatsapp_instance)
        session.last_activity_time = datetime.now()
        if whatsapp_instance:
            session.whatsapp_instance = whatsapp_instance

        session.chat_history.append({"role": "user", "content": user_message})

        if user_message.lower() == "voltar":
            response = self._handle_voltar(session)
        elif session.state == ConversationState.HUMAN_ATTENDING:
            response = None
        else:
            handler = self.state_handlers.get(session.state)
            if handler:
                response = await handler.handle(self, session, user_message)
            else:
                logging.error(
                    f"Nenhum handler encontrado para o estado: {session.state}"
                )
                session.reset()
                greeting_handler = self.state_handlers[ConversationState.GREETING]
                response = greeting_handler.get_entry_message(self, session)

        if response:
            session.chat_history.append({"role": "assistant", "content": response})

        return response

    def _get_service_type(self, service: AccountingService) -> str:
        pf_services = [AccountingService.IMPOSTO_RENDA_PF]
        if service in pf_services:
            return "PF"
        return "PJ"

    def _handle_voltar(self, session: UserSession) -> str:
        """
        Lida com o comando 'voltar' delegando a lógica para o handler do estado atual.
        """
        session.client.service = None

        current_handler = self.state_handlers.get(session.state)

        if session.state in [
            ConversationState.ATENDIMENTO_HUMANO,
            ConversationState.HUMAN_ATTENDING,
        ]:
            session.reset()
            new_handler = self.state_handlers[ConversationState.GREETING]
            return new_handler.get_entry_message(self, session)

        new_state = current_handler.handle_back(self, session)

        self._set_state(session, new_state)

        new_handler = self.state_handlers.get(new_state)
        return new_handler.get_entry_message(self, session)

    async def _redirect_to_service_flow(
        self, session: UserSession, service_key: str
    ) -> str:
        pj_handler = self.state_handlers[
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ
        ]
        pf_handler = self.state_handlers[
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF
        ]

        if service_key == AccountingService.REGULARIZACAO_EMPRESA.value:
            return await pj_handler.handle(self, session, "1")
        elif service_key == AccountingService.DEPARTAMENTO_PESSOAL.value:
            return await pj_handler.handle(self, session, "2")
        elif service_key == AccountingService.ABERTURA_EMPRESA.value:
            return await pj_handler.handle(self, session, "3")
        elif service_key == AccountingService.PLANEJAMENTO_PATRIMONIAL.value:
            return await pj_handler.handle(self, session, "4")
        elif service_key == AccountingService.IMPOSTO_RENDA_PF.value:
            return await pf_handler.handle(self, session, "1")
        else:
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session,
                f"IA classificou '{service_key}', mas não há fluxo de redirecionamento.",
            )

    async def _buscar_dados_documento(
        self, session: UserSession, documento: str
    ) -> Optional[CNPJData]:
        return await consultar_cnpj_empresa(documento)

    def _enviar_para_atendente_humano(self, session: UserSession, motivo: str) -> str:
        self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
        resumo = {
            "cliente_nome": session.client.name or "Novo Cliente",
            "servico_nome": session.client.service.value
            if session.client.service
            else "Não especificado",
            "cliente_mensagem": motivo,
            "whatsapp_link": f"https://wa.me/{session.client.user_id}",
        }
        logging.info(f"Direcionamento para humano acionado: {resumo}")

        try:
            from app.core.settings import get_settings

            settings = get_settings()
            self.email_service.send_notification_email(
                resumo, settings.ADMIN_EMAIL_RECIPIENT
            )
        except Exception as e:
            logging.error(f"Falha ao enviar e-mail de notificação: {e}")

        return (
            "Entendido! Já estou chamando um de nossos especialistas para falar com você.\n\n"
            f"Eles receberão o seguinte resumo: *{motivo}*\n\n"
            "Por favor, aguarde que em breve alguém entrará em contato por aqui."
        )

    def set_human_attending(self, user_id: str):
        session = self._get_session(user_id)
        session.last_activity_time = datetime.now()
        if session.state != ConversationState.HUMAN_ATTENDING:
            self._set_state(session, ConversationState.HUMAN_ATTENDING)
            logging.info(f"Sessão do usuário {user_id} definida para HUMAN_ATTENDING.")

    def check_inactivity_and_cleanup(self, inactivity_minutes: int) -> list[str]:
        inactive_user_ids = []
        current_time = datetime.now()
        for user_id, session in list(self.user_sessions.items()):
            if (
                session.state != ConversationState.ATENDIMENTO_HUMANO
                and (current_time - session.last_activity_time).total_seconds()
                > inactivity_minutes * 60
            ):
                inactive_user_ids.append(session)
                logging.info(
                    f"Sessão do usuário {user_id} marcada como inativa. Estado: {session.state}"
                )
        return inactive_user_ids

    def delete_session(self, user_id: str):
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
            logging.info(f"Sessão do usuário {user_id} deletada.")
