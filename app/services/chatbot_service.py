import logging
import re
import asyncio
from typing import Optional
from app.models import Client
from app.models.enums import ConversationState, DocumentType, AccountingService
from app.services.ia_service import IaService
from app.services.email_service import send_email
from app.services.document_service import (
    validar_cpf,
    consultar_cnpj_empresa,
    CNPJData,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class UserSession:
    """
    Classe interna para gerenciar o estado da sessão e os dados do cliente.
    """

    def __init__(self, user_id: str):
        self.client = Client(user_id=user_id)
        self.state = ConversationState.GREETING
        self.previous_state = ConversationState.GREETING
        self.chat_history = []
        self.ia_suggestion = None

    def reset(self):
        """Reseta a sessão para o início."""
        self.state = ConversationState.GREETING
        self.previous_state = ConversationState.GREETING
        self.chat_history = []
        self.ia_suggestion = None
        # (Não limpamos os dados do client, como nome/documento)


class ChatbotService:
    def _get_service_type(self, service: AccountingService) -> str:
        """Determina se um serviço é para Pessoa Física (PF) ou Pessoa Jurídica (PJ)."""
        pf_services = [AccountingService.IMPOSTO_RENDA_PF]
        if service in pf_services:
            return "PF"
        return "PJ"

    def __init__(self, ia: IaService):
        self.user_sessions = {}
        self.ia = ia
        logging.info("ChatbotService iniciado com handlers de estado.")

        # O dispatcher que mapeia cada estado a uma função handler
        self.state_handlers = {
            ConversationState.GREETING: self._handle_greeting,
            ConversationState.AGUARDANDO_OPCAO_INICIAL: self._handle_aguardando_opcao_inicial,
            ConversationState.AGUARDANDO_CPF_CNPJ: self._handle_aguardando_cpf_cnpj,
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF: self._handle_aguardando_escolha_servico_pf,
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ: self._handle_service_choice_pj,
            ConversationState.AGUARDANDO_NOME_PF: self._handle_aguardando_nome_pf,
            ConversationState.SERVICO_DEPTO_PESSOAL_PERGUNTA_1: self._handle_servico_depto_pessoal_pergunta_1,
            ConversationState.SERVICO_ABERTURA_EMPRESA_PERGUNTA_1: self._handle_servico_abertura_empresa_pergunta_1,
            ConversationState.SERVICO_PLANEJAMENTO_MENU: self._handle_servico_planejamento_menu,
            ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION: self._call_ia_fallback,
            ConversationState.SERVICO_IA_CLASSIFY_AWAIT_CONFIRMATION: self._handle_servico_ia_classify_await_confirmation,
            ConversationState.DOUBTS: self._handle_doubts,
            ConversationState.ATENDIMENTO_HUMANO: self._handle_atendimento_humano,
        }

        # Mapeia um estado para a mensagem que o inicia (para a função "Voltar")
        self.state_entry_messages = {
            ConversationState.GREETING: self._menu_inicial,
            ConversationState.AGUARDANDO_OPCAO_INICIAL: self._menu_inicial,
            ConversationState.AGUARDANDO_CPF_CNPJ: "Ok, vamos lá. Por favor, me informe seu CPF (11 números) ou CNPJ (14 números).\n\n*(Digite 'Voltar' para o menu principal)*",
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF: self._menu_servicos_pf,
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ: self._menu_servicos_pj,
            ConversationState.SERVICO_DEPTO_PESSOAL_PERGUNTA_1: "Entendido. Você já possui funcionários registrados? (Sim/Não)\n\n*(Digite 'Voltar' para o menu de serviços)*",
            ConversationState.SERVICO_ABERTURA_EMPRESA_PERGUNTA_1: "Ok. Você já definiu o tipo de empresa (MEI, LTDA, etc.)? (Sim/Não)\n\n*(Digite 'Voltar' para o menu de serviços)*",
            ConversationState.SERVICO_PLANEJAMENTO_MENU: self._menu_planejamento,
            ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION: "Entendido. Por favor, descreva em poucas palavras qual é o seu problema ou necessidade.\n\n*(Digite 'Voltar' para o menu de serviços)*",
            ConversationState.DOUBTS: "Claro, por favor, descreva a sua dúvida e eu farei o meu melhor para responder.\n\n*(Digite 'Voltar' para o menu principal)*",
        }

    def _get_session(self, user_id: str) -> UserSession:
        """Busca ou cria uma sessão de usuário (UserSession)."""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = UserSession(user_id)
            logging.info(f"Nova sessão criada para o usuário: {user_id}")
        return self.user_sessions[user_id]

    def _set_state(self, session: UserSession, new_state: ConversationState):
        """Define o novo estado e salva o anterior para a função 'Voltar'."""
        if session.state != new_state:
            session.previous_state = session.state
        session.state = new_state

    async def process_message(self, user_id: str, user_message: str) -> str:
        """
        Processa a mensagem do usuário, registra o histórico e usa o dispatcher de estados.
        """
        session = self._get_session(user_id)

        session.chat_history.append({"role": "user", "content": user_message})

        if user_message.lower() == "voltar":
            response = self._handle_voltar(session)
        else:
            handler = self.state_handlers.get(session.state)

            if handler:
                # Await async handlers
                if asyncio.iscoroutinefunction(handler):
                    response = await handler(session, user_message)
                else:
                    response = handler(session, user_message)
            else:
                logging.error(
                    f"Nenhum handler encontrado para o estado: {session.state}"
                )
                session.reset()
                response = self._menu_inicial(session)

        session.chat_history.append({"role": "assistant", "content": response})

        return response

    # --- Handlers de Estado (Lógica de cada etapa da conversa) ---

    def _handle_greeting(self, session: UserSession, user_message: str) -> str:
        """Handler para o estado inicial, apenas mostra o menu."""
        return self._menu_inicial(session)

    async def _handle_aguardando_opcao_inicial(
        self, session: UserSession, user_message: str
    ) -> str:
        if user_message == "1":
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session, "Usuário novo, precisa de atenção."
            )
        elif user_message == "2":
            self._set_state(session, ConversationState.AGUARDANDO_CPF_CNPJ)
            return "Ok, vamos lá. Por favor, me informe seu CPF (11 números) ou CNPJ (14 números) para eu localizar seu cadastro.\n\n*(Digite 'Voltar' para o menu principal)*"
        elif user_message == "3":
            self._set_state(session, ConversationState.DOUBTS)
            return "Claro, por favor, descreva a sua dúvida e eu farei o meu melhor para responder.\n\n*(Digite 'Voltar' para o menu principal)*"
        else:
            return await self._call_ia_fallback(session, user_message)

    async def _handle_aguardando_cpf_cnpj(
        self, session: UserSession, user_message: str
    ) -> str:
        doc = re.sub(r"\D", "", user_message or "")
        if len(doc) == 11:
            if validar_cpf(doc):
                session.client.document_type = DocumentType.CPF
                session.client.document_number = doc
                if (
                    session.client.service
                    and self._get_service_type(session.client.service) == "PJ"
                ):
                    return (
                        f"Você informou um CPF, mas o serviço selecionado ({session.client.service.value}) é para Pessoa Jurídica. "
                        "Por favor, digite um CNPJ compatível com o serviço, ou digite 'Voltar' para escolher outro serviço.\n\n"
                        "*(Digite 'Voltar' para o menu principal)*"
                    )
                else:
                    self._set_state(session, ConversationState.AGUARDANDO_NOME_PF)
                    return "CPF validado. Por favor, digite seu nome completo para prosseguirmos.\n\n*(Digite 'Voltar' para o menu principal)*"
        if len(doc) == 14:
            dados = await self._buscar_dados_documento(session, doc)
            print(dados)
            if dados and dados.sucesso:
                session.client.document_type = DocumentType.CNPJ
                session.client.document_number = doc
                company_name = None
                if dados.razao_social:
                    company_name = dados.razao_social
                elif dados.nome_fantasia:
                    company_name = dados.nome_fantasia
                print(dados)
                if company_name:
                    session.client.name = company_name
                    print(session.client.name, company_name, dados.razao_social)
                    response = f"Olá! Encontrei o cadastro da empresa: {session.client.name}.\n\n"
                else:
                    response = "Não localizei a razão social ou nome fantasia, mas pode ser um erro no sistema. Vamos prosseguir.\n\n"

                if (
                    session.client.service
                    and self._get_service_type(session.client.service) == "PF"
                ):
                    return (
                        f"Você informou um CNPJ, mas o serviço selecionado ({session.client.service.value}) é para Pessoa Física. "
                        "Por favor, digite um CPF compatível com o serviço, ou digite 'Voltar' para escolher outro serviço.\n\n"
                        "*(Digite 'Voltar' para o menu principal)*"
                    )
                elif session.client.service:
                    return await self._redirect_to_service_flow(
                        session, session.client.service.value
                    )
                else:
                    self._set_state(
                        session, ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ
                    )
                    return response + self._menu_servicos_pj(session)
        else:
            return "Número de documento inválido. Por favor, digite um CPF (11 números) ou CNPJ (14 números).\n\n*(Digite 'Voltar' para o menu principal)*"

    async def _handle_aguardando_nome_pf(
        self, session: UserSession, user_message: str
    ) -> str:
        session.client.name = user_message.strip()
        if session.client.service:
            return await self._redirect_to_service_flow(
                session, session.client.service.value
            )
        self._set_state(session, ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF)
        return (
            f"Obrigado, {session.client.name}! Agora, por favor, escolha o serviço desejado:\n\n"
            + self._menu_servicos_pf(session)
        )

    async def _handle_aguardando_escolha_servico_pf(
        self, session: UserSession, user_message: str
    ) -> str:
        if user_message == "1":
            session.client.service = AccountingService.IMPOSTO_RENDA_PF
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session, "Solicitou: Imposto de Renda Pessoa Física."
            )
        else:
            return await self._call_ia_fallback(session, user_message)

    def _handle_servico_depto_pessoal_pergunta_1(
        self, session: UserSession, user_message: str
    ) -> str:
        contexto = (
            f"Solicitou: Departamento Pessoal. (Já possui funcionários: {user_message})"
        )
        self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
        return self._enviar_para_atendente_humano(session, contexto)

    def _handle_servico_abertura_empresa_pergunta_1(
        self, session: UserSession, user_message: str
    ) -> str:
        contexto = (
            f"Solicitou: Abertura de Empresa. (Já definiu o tipo: {user_message})"
        )
        self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
        return self._enviar_para_atendente_humano(session, contexto)

    async def _handle_servico_planejamento_menu(
        self, session: UserSession, user_message: str
    ) -> str:
        if user_message == "1":
            session.client.service = AccountingService.PLANEJAMENTO_REDUZIR_CARGA
            contexto = "Solicitou: Planejamento (Reduzir carga tributária)"
        elif user_message == "2":
            session.client.service = AccountingService.PLANEJAMENTO_REESTRUTURAR_REGIME
            contexto = "Solicitou: Planejamento (Reestruturar regime)"
        elif user_message == "3":
            session.client.service = (
                AccountingService.PLANEJAMENTO_CONSULTORIA_PREVENTIVA
            )
            contexto = "Solicitou: Planejamento (Consultoria preventiva)"
        elif user_message == "4":
            session.client.service = AccountingService.PLANEJAMENTO_REVISAR_TRIBUTOS
            contexto = "Solicitou: Planejamento (Revisar tributos pagos)"
        else:
            return await self._call_ia_fallback(session, user_message)

        self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
        return self._enviar_para_atendente_humano(session, contexto)

    async def _handle_servico_ia_classify_await_confirmation(
        self, session: UserSession, user_message: str
    ) -> str:
        if user_message.lower() in ["sim", "s"]:
            session.client.service = AccountingService(session.ia_suggestion)
            logging.info(f"Usuário aceitou a sugestão da IA: {session.ia_suggestion}")
            if session.client.document_number:
                return await self._redirect_to_service_flow(
                    session, session.client.service.value
                )
            self._set_state(session, ConversationState.AGUARDANDO_CPF_CNPJ)
            return self.state_entry_messages.get(session.state)
        else:
            return (
                "Entendido. Desculpe pelo engano. Estou te encaminhando para um de nossos especialistas para entender melhor sua necessidade.\n\n"
                + self._enviar_para_atendente_humano(
                    session,
                    f"IA sugeriu '{session.ia_suggestion}', usuário recusou.",
                )
            )

    def _handle_doubts(self, session: UserSession, user_message: str) -> str:
        """Chama a IA para responder uma dúvida e depois transiciona para o atendimento humano para evitar loops."""
        ia_result = self.ia.handle_ai_request(session.chat_history, session.state)

        self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)

        if ia_result["status"] == "fail":
            return (
                ia_result["content"]
                + "\n\nPara garantir que você seja atendido, estou te encaminhando para um de nossos especialistas."
            )

        return (
            ia_result["content"]
            + "\n\nEspero ter ajudado! Se precisar de mais alguma coisa, um de nossos especialistas já foi acionado para falar com você."
        )

    def _handle_atendimento_humano(
        self, session: UserSession, user_message: str
    ) -> str:
        return "Você já está na fila para o atendimento humano. Por favor, aguarde mais um momento que um especialista logo falará com você.\n\n*(Se desejar recomeçar do zero, digite 'Voltar')*"

    def _handle_voltar(self, session: UserSession) -> str:
        """Lida com o comando 'voltar', retornando ao estado anterior."""
        if session.state == ConversationState.SERVICO_IA_CLASSIFY_AWAIT_CONFIRMATION:
            self._set_state(
                session, ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
            )
            entry_message_or_func = self.state_entry_messages.get(session.state)
            if callable(entry_message_or_func):
                return entry_message_or_func(session)
            elif isinstance(entry_message_or_func, str):
                return entry_message_or_func
            else:
                session.reset()
                return self._menu_inicial(session)

        self._set_state(session, session.previous_state)

        entry_message_or_func = self.state_entry_messages.get(session.state)

        if callable(entry_message_or_func):
            return entry_message_or_func(session)
        elif isinstance(entry_message_or_func, str):
            return entry_message_or_func
        else:
            session.reset()
            return self._menu_inicial(session)

    async def _call_ia_fallback(self, session: UserSession, user_message: str) -> str:
        logging.info(f"Chamando IA como fallback para o estado: {session.state}")
        past = session.state  # Reintroduce past
        current_fallback_state = session.state
        logging.info(f"Type of self.ia: {type(self.ia)}, Value of self.ia: {self.ia}")
        ia_result = self.ia.handle_ai_request(
            session.chat_history, current_fallback_state
        )
        if ia_result is None:
            logging.error(
                f"ia_result is None from handle_ai_request for user: {session.client.user_id}"
            )
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session,
                f"Erro interno: IA retornou valor nulo para a mensagem '{user_message}'.",
            )

        if ia_result["type"] == "answer":
            self._set_state(
                session, ConversationState.ATENDIMENTO_HUMANO
            )  # Transition to human assistance after answering a doubt
            return ia_result["content"]

        # Handle classification results
        if current_fallback_state == ConversationState.AGUARDANDO_OPCAO_INICIAL:
            if ia_result.get("service") and ia_result.get("service") in [
                s.value for s in AccountingService
            ]:
                session.ia_suggestion = ia_result["service"]
                self._set_state(
                    session, ConversationState.AGUARDANDO_CPF_CNPJ
                )  # Go to CPF/CNPJ after initial service classification
                return (
                    f"Entendido. Pela sua descrição, parece que você precisa de: **{ia_result['service']}**.\n\n"
                    f"*{ia_result['description']}*\n\n"
                    "Para prosseguir, por favor, informe seu CPF (11 números) ou CNPJ (14 números).\n\n"
                    "*(Digite 'Voltar' para o menu principal)*"
                )
            elif ia_result.get("option") and ia_result.get("option") != "None":
                logging.info(
                    f"IA classificou a opção: {ia_result.get('option')}. Reprocessando..."
                )
                session.chat_history.pop()  # Remove the current user message from history before re-processing
                session.state = past  # Revert to the state before fallback
                return await self.process_message(
                    session.client.user_id, ia_result.get("option")
                )
            else:
                logging.warning(
                    f"IA fallback para AGUARDANDO_OPCAO_INICIAL falhou ou retornou classificação inesperada. "
                    f"IA Result: {ia_result}"
                )
                self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
                return self._enviar_para_atendente_humano(
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
                session.chat_history.pop()  # Remove the current user message from history before re-processing
                session.state = past  # Revert to the state before fallback
                return await self.process_message(
                    session.client.user_id, ia_result.get("option")
                )
            else:
                logging.warning(
                    f"IA fallback para menu de serviços falhou ou retornou classificação inesperada. "
                    f"IA Result: {ia_result}"
                )
                self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
                return self._enviar_para_atendente_humano(
                    session,
                    f"IA não conseguiu classificar a opção de serviço para a mensagem '{user_message}'.",
                )
        elif (
            current_fallback_state
            == ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
        ):
            if ia_result.get("service") and ia_result.get("service") != "OUTRO":
                session.ia_suggestion = ia_result["service"]
                self._set_state(
                    session, ConversationState.SERVICO_IA_CLASSIFY_AWAIT_CONFIRMATION
                )
                return (
                    f"Entendido. Pela sua descrição, parece que você precisa de: **{ia_result['service']}**.\n\n"
                    f"*{ia_result['description']}*\n\n"
                    "Isso está correto? (Sim/Não)\n\n"
                    "*(Digite 'Voltar' para descrever novamente)*"
                )
            elif ia_result.get("option") and ia_result.get("option") != "None":
                logging.info(
                    f"IA classificou a opção: {ia_result.get('option')}. Reprocessando..."
                )
                session.chat_history.pop()
                session.state = past
                return await self.process_message(
                    session.client.user_id, ia_result.get("option")
                )
            else:
                logging.warning(
                    f"IA fallback falhou ou retornou classificação inesperada para o estado {session.state}. "
                    f"IA Result: {ia_result}"
                )
                self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
                return self._enviar_para_atendente_humano(
                    session,
                    f"IA não conseguiu responder à mensagem '{user_message}' no estado '{session.state}'.",
                )
        else:
            logging.warning(
                f"IA fallback para estado não tratado ({current_fallback_state}) ou retornou classificação inesperada. "
                f"IA Result: {ia_result}"
            )
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session,
                f"IA não conseguiu responder à mensagem '{user_message}' no estado '{session.state}'.",
            )

    # --- Funções Auxiliares (Menus, Redirecionamento, etc.) ---

    async def _redirect_to_service_flow(
        self, session: UserSession, service_key: str
    ) -> str:
        """Redireciona o usuário para o início do sub-fluxo de serviço após a confirmação da IA."""
        if service_key == AccountingService.REGULARIZACAO_EMPRESA.value:
            return await self._handle_service_choice_pj(session, "1")
        elif service_key == AccountingService.DEPARTAMENTO_PESSOAL.value:
            return await self._handle_service_choice_pj(session, "2")
        elif service_key == AccountingService.ABERTURA_EMPRESA.value:
            return await self._handle_service_choice_pj(session, "3")
        elif service_key == AccountingService.PLANEJAMENTO_PATRIMONIAL.value:
            return await self._handle_service_choice_pj(session, "4")
        elif service_key == AccountingService.IMPOSTO_RENDA_PF.value:
            return await self._handle_aguardando_escolha_servico_pf(session, "1")
        else:
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session,
                f"IA classificou '{service_key}', mas não há fluxo de redirecionamento.",
            )

    async def _handle_service_choice_pj(
        self, session: UserSession, user_message: str
    ) -> str:
        """Processa a escolha do menu de Serviços PJ. Reutilizado por outros handlers."""
        if user_message == "1":
            session.client.service = AccountingService.REGULARIZACAO_EMPRESA
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session, "Solicitou: Regularização de Empresa."
            )
        elif user_message == "2":
            session.client.service = AccountingService.DEPARTAMENTO_PESSOAL
            self._set_state(session, ConversationState.SERVICO_DEPTO_PESSOAL_PERGUNTA_1)
            return "Entendido. Você já possui funcionários registrados? (Sim/Não)\n\n*(Digite 'Voltar' para o menu de serviços)*"
        elif user_message == "3":
            session.client.service = AccountingService.ABERTURA_EMPRESA
            self._set_state(
                session, ConversationState.SERVICO_ABERTURA_EMPRESA_PERGUNTA_1
            )
            return "Ok. Você já definiu o tipo de empresa (MEI, LTDA, etc.)? (Sim/Não)\n\n*(Digite 'Voltar' para o menu de serviços)*"
        elif user_message == "4":
            session.client.service = AccountingService.PLANEJAMENTO_PATRIMONIAL
            self._set_state(session, ConversationState.SERVICO_PLANEJAMENTO_MENU)
            return self._menu_planejamento(session)
        elif user_message == "5":
            self._set_state(
                session, ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
            )
            return "Entendido. Por favor, descreva em poucas palavras qual é o seu problema ou necessidade para que eu possa te ajudar a encontrar o serviço certo.\n\n*(Digite 'Voltar' para o menu de serviços)*"
        else:
            return await self._call_ia_fallback(session, user_message)

    # --- Funções de Menu (Textos) ---

    def _menu_inicial(self, session, add_stage=True):
        if add_stage:
            self._set_state(session, ConversationState.AGUARDANDO_OPCAO_INICIAL)
        greeting = "Olá"
        if session.client.name:
            greeting += f", {session.client.name}"
        greeting += "! Bem-vindo(a) ao atendimento da DAS Contabilidade.\n"
        return (
            f"{greeting}\n"
            "Eu sou o CountBelly, seu assistente virtual.\n\n"
            "Como posso te ajudar hoje?\n\n"
            "1. Sou novo por aqui.\n"
            "2. Preciso de um serviço específico.\n"
            "3. Tenho uma dúvida.\n\n"
            "*(Digite o número da opção desejada)*"
        )

    def _menu_servicos_pf(self, session, add_stage=True):
        if add_stage:
            self._set_state(session, ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF)
        greeting = ""
        if session.client.name:
            greeting = f"Olá, {session.client.name}! "
        return (
            f"{greeting}Serviços disponíveis para CPF:\n\n"
            "1. Imposto de Renda Pessoa Física\n\n"
            "*(Digite o número da opção ou 'Voltar')*"
        )

    def _menu_servicos_pj(self, session, add_stage=True):
        """Menu específico para Pessoa Jurídica."""
        if add_stage:
            self._set_state(session, ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ)
        greeting = ""
        if session.client.name:
            greeting = f"Olá, {session.client.name}! "
        return (
            f"{greeting}Serviços disponíveis para CNPJ:\n\n"
            "1. Regularização de Empresa\n"
            "2. Departamento Pessoal (eSocial, etc.)\n"
            "3. Abertura de Empresa\n"
            "4. Planejamento Patrimonial e Sucessório\n"
            "5. Outro (Não sei qual escolher)\n\n"
            "*(Digite o número da opção ou 'Voltar')*"
        )

    def _menu_planejamento(self, session, add_stage=True):
        if add_stage:
            self._set_state(session, ConversationState.SERVICO_PLANEJAMENTO_MENU)
        return (
            "Qual o seu objetivo com o Planejamento?\n\n"
            "1. Reduzir legalmente a carga tributária\n"
            "2. Reestruturar seu regime de tributação\n"
            "3. Obter consultoria preventiva\n"
            "4. Revisar tributos pagos nos últimos anos\n\n"
            "*(Digite o número da opção ou 'Voltar')*"
        )

    # --- Placeholders para Integração com DB e outros services ---

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
            "whatsapp_link": f"https://wa.me/{session.client.user_id}",  # Assuming user_id is a phone number
        }

        logging.info(f"Direcionamento para humano acionado: {resumo}")
        send_email(resumo)
        return (
            "Entendido! Já estou chamando um de nossos especialistas para falar com você.\n\n"
            f"Eles receberão o seguinte resumo: *{motivo}*\n\n"
            "Por favor, aguarde que em breve alguém entrará em contato por aqui."
        )
