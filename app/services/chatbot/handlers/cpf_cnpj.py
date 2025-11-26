import re
from typing import TYPE_CHECKING
from app.models.enums import ConversationState, DocumentType
from app.services.document_service import validar_cpf
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class CpfCnpjHandler(StateHandler):
    """Handler para o estado que aguarda o CPF ou CNPJ do usuário."""

    async def handle(
        self,
        service: "ChatbotService",
        session: "UserSession",
        user_message: str,
    ) -> str:
        doc = re.sub(r"\D", "", user_message or "")

        if len(doc) == 11:
            return await self._handle_cpf(service, session, doc)

        if len(doc) == 14:
            return await self._handle_cnpj(service, session, doc)

        return "Número de documento inválido. Por favor, digite um CPF (11 números) ou CNPJ (14 números).\n\n*(Digite 'Voltar' para o menu principal)*"

    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        return "Ok, vamos lá. Por favor, me informe seu CPF (11 números) ou CNPJ (14 números) para eu localizar seu cadastro.\n\n*(Digite 'Voltar' para o menu principal)*"

    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        return ConversationState.AGUARDANDO_OPCAO_INICIAL

    async def _handle_cpf(
        self, service: "ChatbotService", session: "UserSession", doc: str
    ) -> str:
        if not validar_cpf(doc):
            return "CPF inválido. Por favor, verifique os números e tente novamente.\n\n*(Digite 'Voltar' para o menu principal)*"

        session.client.document_type = DocumentType.CPF
        session.client.document_number = doc

        if (
            session.client.service
            and service._get_service_type(session.client.service) == "PJ"
        ):
            return (
                f"Você informou um CPF, mas o serviço selecionado ({session.client.service.value}) é para Pessoa Jurídica. "
                "Por favor, digite um CNPJ compatível com o serviço, ou digite 'Voltar' para escolher outro serviço.\n\n"
                "*(Digite 'Voltar' para o menu principal)*"
            )

        service._set_state(session, ConversationState.AGUARDANDO_NOME_PF)
        new_handler = service.state_handlers[ConversationState.AGUARDANDO_NOME_PF]
        return new_handler.get_entry_message(service, session)

    async def _handle_cnpj(
        self, service: "ChatbotService", session: "UserSession", doc: str
    ) -> str:
        dados = await service._buscar_dados_documento(session, doc)
        if not (dados and dados.sucesso):
            return "Não consegui validar o CNPJ ou encontrar dados da empresa. Por favor, verifique o número e tente novamente.\n\n*(Digite 'Voltar' para o menu principal)*"

        session.client.document_type = DocumentType.CNPJ
        session.client.document_number = doc

        company_name = dados.razao_social or dados.nome_fantasia
        if company_name:
            session.client.name = company_name
            response = (
                f"Olá! Encontrei o cadastro da empresa: {session.client.name}.\n\n"
            )
        else:
            response = "Não localizei a razão social ou nome fantasia, mas pode ser um erro no sistema. Vamos prosseguir.\n\n"

        if (
            session.client.service
            and service._get_service_type(session.client.service) == "PF"
        ):
            return (
                f"Você informou um CNPJ, mas o serviço selecionado ({session.client.service.value}) é para Pessoa Física. "
                "Por favor, digite um CPF compatível com o serviço, ou digite 'Voltar' para escolher outro serviço.\n\n"
                "*(Digite 'Voltar' para o menu principal)*"
            )

        if session.client.service:
            return await service._redirect_to_service_flow(
                session, session.client.service.value
            )

        service._set_state(session, ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ)
        new_handler = service.state_handlers[
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ
        ]
        return response + new_handler.get_entry_message(service, session)
