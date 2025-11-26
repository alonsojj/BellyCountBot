import logging
from typing import TYPE_CHECKING
from app.models.enums import ConversationState, AccountingService
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class IaClassifyAwaitDescriptionHandler(StateHandler):
    """
    Handler para o estado onde a IA tenta classificar a descrição do usuário
    ou age como fallback geral.
    """

    async def handle(
        self,
        service: "ChatbotService",
        session: "UserSession",
        user_message: str,
    ) -> str:
        logging.info(f"Chamando IA como fallback para o estado: {session.state}")
        current_fallback_state = session.state
        ia_result = service.ia.handle_ai_request(
            session.chat_history, current_fallback_state
        )
        if ia_result is None:
            logging.error(
                f"IA retornou 'None' para o usuário: {session.client.user_id}"
            )
            service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return service._enviar_para_atendente_humano(
                session,
                f"Erro interno: IA retornou valor nulo para a mensagem '{user_message}'.",
            )
        if ia_result["type"] == "answer":
            service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return ia_result["content"]

        if current_fallback_state == ConversationState.AGUARDANDO_OPCAO_INICIAL:
            if ia_result.get("service") and ia_result.get("service") in [
                s.value for s in AccountingService
            ]:
                session.ia_suggestion = ia_result["service"]
                session.client.service = AccountingService(session.ia_suggestion)
                service._set_state(session, ConversationState.AGUARDANDO_CPF_CNPJ)
                new_handler = service.state_handlers[
                    ConversationState.AGUARDANDO_CPF_CNPJ
                ]
                return (
                    f"Entendido. Pela sua descrição, parece que você precisa de: **{ia_result['service']}**.\n\n"
                    f"*{ia_result['description']}*\n\n"
                    + new_handler.get_entry_message(service, session)
                )
            elif ia_result.get("option") and ia_result.get("option") != "None":
                logging.info(
                    f"IA classificou a opção: {ia_result.get('option')}. Reprocessando..."
                )
                session.chat_history.pop()
                return await service.process_message(
                    session.client.user_id, ia_result.get("option")
                )
            else:
                logging.warning(
                    f"IA fallback para AGUARDANDO_OPCAO_INICIAL falhou ou retornou classificação inesperada. "
                    f"IA Result: {ia_result}"
                )
                service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
                return service._enviar_para_atendente_humano(
                    session,
                    f"IA não conseguiu classificar o serviço ou opção inicial para a mensagem '{user_message}'.",
                )
        elif current_fallback_state in [
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF,
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ,
        ]:
            if ia_result.get("option") and ia_result.get("option") != "None":
                logging.info(
                    f"IA classificou a opção: {ia_result.get('option')}. Reprocessando..."
                )
                session.chat_history.pop()
                return await service.process_message(
                    session.client.user_id, ia_result.get("option")
                )
            else:
                logging.warning(
                    f"IA fallback para menu de serviços falhou ou retornou classificação inesperada. "
                    f"IA Result: {ia_result}"
                )
                service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
                return service._enviar_para_atendente_humano(
                    session,
                    f"IA não conseguiu classificar a opção de serviço para a mensagem '{user_message}'.",
                )
        elif (
            current_fallback_state
            == ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
        ):
            if ia_result.get("service") and ia_result.get("service") != "OUTRO":
                session.ia_suggestion = ia_result["service"]
                service._set_state(
                    session, ConversationState.SERVICO_IA_CLASSIFY_AWAIT_CONFIRMATION
                )
                new_handler = service.state_handlers[
                    ConversationState.SERVICO_IA_CLASSIFY_AWAIT_CONFIRMATION
                ]
                return new_handler.get_entry_message(service, session)
            elif ia_result.get("option") and ia_result.get("option") != "None":
                logging.info(
                    f"IA classificou a opção: {ia_result.get('option')}. Reprocessando..."
                )
                session.chat_history.pop()
                return await service.process_message(
                    session.client.user_id, ia_result.get("option")
                )
            else:
                logging.warning(
                    f"IA fallback falhou ou retornou classificação inesperada para o estado {session.state}. "
                    f"IA Result: {ia_result}"
                )
                service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
                return service._enviar_para_atendente_humano(
                    session,
                    f"IA não conseguiu responder à mensagem '{user_message}' no estado '{session.state}'.",
                )
        else:
            logging.warning(
                f"IA fallback para estado não tratado ({current_fallback_state}) ou retornou classificação inesperada. "
                f"IA Result: {ia_result}"
            )
            service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return service._enviar_para_atendente_humano(
                session,
                f"IA não conseguiu responder à mensagem '{user_message}' no estado '{session.state}'.",
            )

    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        return "Entendido. Por favor, descreva em poucas palavras qual é o seu problema ou necessidade para que eu possa te ajudar a encontrar o serviço certo.\n\n*(Digite 'Voltar' para o menu de serviços)*"

    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        return ConversationState.AGUARDANDO_OPCAO_INICIAL
