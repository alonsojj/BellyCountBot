# app/services/chatbot/handlers/pj_service_choice.py
from typing import TYPE_CHECKING
from app.models.enums import ConversationState, AccountingService
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class PjServiceChoiceHandler(StateHandler):
    """Handler para processar a escolha do menu de Serviços PJ."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        if user_message == "1":
            session.client.service = AccountingService.REGULARIZACAO_EMPRESA
            service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return service._enviar_para_atendente_humano(
                session, "Solicitou: Regularização de Empresa."
            )
        elif user_message == "2":
            session.client.service = AccountingService.DEPARTAMENTO_PESSOAL
            service._set_state(
                session, ConversationState.SERVICO_DEPTO_PESSOAL_PERGUNTA_1
            )
            return "Entendido. Você já possui funcionários registrados? (Sim/Não)\n\n*(Digite 'Voltar' para o menu de serviços)*"
        elif user_message == "3":
            session.client.service = AccountingService.ABERTURA_EMPRESA
            service._set_state(
                session, ConversationState.SERVICO_ABERTURA_EMPRESA_PERGUNTA_1
            )
            return "Ok. Você já definiu o tipo de empresa (MEI, LTDA, etc.)? (Sim/Não)\n\n*(Digite 'Voltar' para o menu de serviços)*"
        elif user_message == "4":
            session.client.service = AccountingService.PLANEJAMENTO_PATRIMONIAL
            service._set_state(session, ConversationState.SERVICO_PLANEJAMENTO_MENU)
            return service._menu_planejamento(session)
        elif user_message == "5":
            service._set_state(
                session, ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
            )
            return "Entendido. Por favor, descreva em poucas palavras qual é o seu problema ou necessidade para que eu possa te ajudar a encontrar o serviço certo.\n\n*(Digite 'Voltar' para o menu de serviços)*"
        else:
            return await service._call_ia_fallback(session, user_message)
