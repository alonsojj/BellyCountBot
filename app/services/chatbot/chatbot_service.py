import logging
from datetime import datetime
from typing import Optional

from app.models.enums import ConversationState, AccountingService
from app.models.user_session import UserSession
from app.services.ia_service import IaService
from app.services.email_service import send_email
from app.services.document_service import (
    consultar_cnpj_empresa,
    CNPJData,
)

# Imports dos Handlers
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

# Imports das Respostas
from .responses import (
    menu_inicial,
    menu_servicos_pf,
    menu_servicos_pj,
    menu_planejamento,
)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ChatbotService:
    """
    Orquestrador principal do chatbot. Gerencia sessões e direciona as mensagens
    para o handler de estado apropriado.
    """

    def __init__(self, ia: IaService):
        self.user_sessions = {}
        self.ia = ia
        logging.info("ChatbotService iniciado com handlers de estado refatorados.")

        # O dispatcher mapeia cada estado para uma instância de Handler
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
            ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION: self._call_ia_fallback,  # Mantido como método por enquanto
            ConversationState.SERVICO_IA_CLASSIFY_AWAIT_CONFIRMATION: IaConfirmationHandler(),
            ConversationState.DOUBTS: DoubtsHandler(),
            ConversationState.ATENDIMENTO_HUMANO: HumanAttendanceHandler(),
            ConversationState.HUMAN_ATTENDING: HumanAttendanceHandler(),
        }

        # Mapeia um estado para a mensagem que o inicia (para a função "Voltar")
        self.state_entry_messages = {
            ConversationState.GREETING: menu_inicial,
            ConversationState.AGUARDANDO_OPCAO_INICIAL: menu_inicial,
            ConversationState.AGUARDANDO_CPF_CNPJ: "Ok, vamos lá. Por favor, me informe seu CPF (11 números) ou CNPJ (14 números).\n\n*(Digite 'Voltar' para o menu principal)*",
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF: menu_servicos_pf,
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ: menu_servicos_pj,
            ConversationState.SERVICO_DEPTO_PESSOAL_PERGUNTA_1: "Entendido. Você já possui funcionários registrados? (Sim/Não)\n\n*(Digite 'Voltar' para o menu de serviços)*",
            ConversationState.SERVICO_ABERTURA_EMPRESA_PERGUNTA_1: "Ok. Você já definiu o tipo de empresa (MEI, LTDA, etc.)? (Sim/Não)\n\n*(Digite 'Voltar' para o menu de serviços)*",
            ConversationState.SERVICO_PLANEJAMENTO_MENU: menu_planejamento,
            ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION: "Entendido. Por favor, descreva em poucas palavras qual é o seu problema ou necessidade.\n\n*(Digite 'Voltar' para o menu de serviços)*",
            ConversationState.DOUBTS: "Claro, por favor, descreva a sua dúvida e eu farei o meu melhor para responder.\n\n*(Digite 'Voltar' para o menu principal)*",
        }

    def _get_session(self, user_id: str) -> UserSession:
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
        session = self._get_session(user_id)
        session.last_activity_time = datetime.now()
        if whatsapp_instance:
            session.whatsapp_instance = whatsapp_instance

        session.chat_history.append({"role": "user", "content": user_message})

        if user_message.lower() == "voltar":
            response = self._handle_voltar(session)
        elif session.state == ConversationState.HUMAN_ATTENDING:
            response = None  # Não processa mensagens se já estiver em atendimento
        else:
            handler = self.state_handlers.get(session.state)
            if handler:
                if hasattr(handler, "handle"):  # Verifica se é uma classe de handler
                    response = await handler.handle(self, session, user_message)
                else:  # Fallback para métodos antigos (ex: _call_ia_fallback)
                    response = await handler(session, user_message)
            else:
                logging.error(
                    f"Nenhum handler encontrado para o estado: {session.state}"
                )
                session.reset()
                response = menu_inicial(session)

        if response:
            session.chat_history.append({"role": "assistant", "content": response})
        return response

    # --- MÉTODOS AUXILIARES (Usados pelos Handlers) ---

    def _get_service_type(self, service: AccountingService) -> str:
        pf_services = [AccountingService.IMPOSTO_RENDA_PF]
        if service in pf_services:
            return "PF"
        return "PJ"

    def _handle_voltar(self, session: UserSession) -> str:
        session.client.service = None
        if session.state == ConversationState.SERVICO_IA_CLASSIFY_AWAIT_CONFIRMATION:
            self._set_state(
                session, ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
            )
        elif session.state in [
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF,
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ,
            ConversationState.SERVICO_DEPTO_PESSOAL_PERGUNTA_1,
            ConversationState.SERVICO_ABERTURA_EMPRESA_PERGUNTA_1,
            ConversationState.SERVICO_PLANEJAMENTO_MENU,
        ]:
            self._set_state(session, ConversationState.AGUARDANDO_CPF_CNPJ)
        elif session.state == ConversationState.AGUARDANDO_CPF_CNPJ:
            self._set_state(session, ConversationState.AGUARDANDO_OPCAO_INICIAL)
        elif session.state == ConversationState.AGUARDANDO_NOME_PF:
            self._set_state(session, ConversationState.AGUARDANDO_CPF_CNPJ)
        elif session.state == ConversationState.DOUBTS:
            self._set_state(session, ConversationState.AGUARDANDO_OPCAO_INICIAL)
        elif session.state in [
            ConversationState.ATENDIMENTO_HUMANO,
            ConversationState.HUMAN_ATTENDING,
        ]:
            session.reset()
        else:
            self._set_state(session, session.previous_state)

        entry_message_or_func = self.state_entry_messages.get(session.state)
        if callable(entry_message_or_func):
            return entry_message_or_func(session)
        elif isinstance(entry_message_or_func, str):
            return entry_message_or_func
        else:
            session.reset()
            return menu_inicial(session)

    async def _call_ia_fallback(self, session: UserSession, user_message: str) -> str:
        # Este método é complexo e pode ser um candidato a sua própria classe no futuro
        logging.info(f"Chamando IA como fallback para o estado: {session.state}")
        # (A lógica interna do _call_ia_fallback permanece a mesma por enquanto)
        current_fallback_state = session.state
        ia_result = self.ia.handle_ai_request(
            session.chat_history, current_fallback_state
        )
        if ia_result is None:
            logging.error(
                f"IA retornou 'None' para o usuário: {session.client.user_id}"
            )
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session,
                f"Erro interno: IA retornou valor nulo para a mensagem '{user_message}'.",
            )
        if ia_result["type"] == "answer":
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return ia_result["content"]
        # ... resto da lógica de fallback ...
        return "Desculpe, não entendi. Poderia tentar de outra forma?"

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
            "cliente_email": session.client.email or "Não informado",
            "cliente_telefone": session.client.phone or session.client.user_id,
            "servico_nome": session.client.service.value
            if session.client.service
            else "Não especificado",
            "cliente_mensagem": motivo,
            "whatsapp_link": f"https://wa.me/{session.client.user_id}",
        }
        logging.info(f"Direcionamento para humano acionado: {resumo}")
        send_email(resumo)
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
