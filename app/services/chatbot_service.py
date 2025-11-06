import logging
import re
from app.models import Client
from app.models.enums import ConversationState, DocumentType, AccountingService
from app.services.ia_service import IaService
from app.services.email_service import send_email

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
            ConversationState.SERVICO_DEPTO_PESSOAL_PERGUNTA_1: self._handle_servico_depto_pessoal_pergunta_1,
            ConversationState.SERVICO_ABERTURA_EMPRESA_PERGUNTA_1: self._handle_servico_abertura_empresa_pergunta_1,
            ConversationState.SERVICO_PLANEJAMENTO_MENU: self._handle_servico_planejamento_menu,
            ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION: self._handle_servico_ia_classify_await_description,
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

    def process_message(self, user_id: str, user_message: str) -> str:
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

    def _handle_aguardando_opcao_inicial(
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
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session, f"Usuário não escolheu opção e disse: '{user_message}'"
            )

    def _handle_aguardando_cpf_cnpj(
        self, session: UserSession, user_message: str
    ) -> str:
        doc = re.sub(r"[^\d]", "", user_message)

        if len(doc) == 11:
            session.client.document_type = DocumentType.CPF
            session.client.document_number = doc
            if not self._validar_cpf(doc):
                logging.warning(f"CPF inválido fornecido: {doc}")

            dados = self._buscar_dados_documento(doc)
            if dados and dados.get("nome"):
                session.client.name = dados["nome"]
                response = f"Olá, {session.client.name}! Cadastro localizado.\n\n"
            else:
                response = "Não localizei seu nome, mas pode ser um erro no sistema. Vamos prosseguir.\n\n"

            self._set_state(session, ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF)
            return response + self._menu_servicos_pf(session)

        elif len(doc) == 14:
            session.client.document_type = DocumentType.CNPJ
            session.client.document_number = doc
            if not self._validar_cnpj(doc):
                logging.warning(f"CNPJ inválido fornecido: {doc}")

            dados = self._buscar_dados_documento(doc)
            if dados and dados.get("nome"):
                session.client.name = dados["nome"]
                response = (
                    f"Olá! Encontrei o cadastro da empresa: {session.client.name}.\n\n"
                )
            else:
                response = "Não localizei a razão social, mas pode ser um erro no sistema. Vamos prosseguir.\n\n"

            self._set_state(session, ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ)
            return response + self._menu_servicos_pj(session)

        else:
            return "Número de documento inválido. Por favor, digite um CPF (11 números) ou CNPJ (14 números).\n\n*(Digite 'Voltar' para o menu principal)*"

    def _handle_aguardando_escolha_servico_pf(
        self, session: UserSession, user_message: str
    ) -> str:
        if user_message == "1":
            session.client.service = AccountingService.IMPOSTO_RENDA_PF
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session, "Solicitou: Imposto de Renda Pessoa Física."
            )
        else:
            return "Opção inválida.\n" + self._menu_servicos_pf(
                session, add_stage=False
            )

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

    def _handle_servico_planejamento_menu(
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
            return "Opção inválida.\n" + self._menu_planejamento(
                session, add_stage=False
            )

        self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
        return self._enviar_para_atendente_humano(session, contexto)

    def _handle_servico_ia_classify_await_description(
        self, session: UserSession, user_message: str
    ) -> str:
        ia_result = self.ia.handle_ai_request(session.chat_history, session.state)

        if ia_result.get("status") == "fail" or ia_result.get("service") == "OUTRO":
            return (
                "Desculpe, não consegui identificar um serviço específico para sua necessidade. Estou te encaminhando para um de nossos especialistas para te ajudar melhor.\n\n"
                + self._enviar_para_atendente_humano(
                    session,
                    f"Falha na classificação da IA.",
                )
            )

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

    def _handle_servico_ia_classify_await_confirmation(
        self, session: UserSession, user_message: str
    ) -> str:
        if user_message.lower() in ["sim", "s"]:
            service_key = session.ia_suggestion
            logging.info(f"Usuário aceitou a sugestão da IA: {service_key}")
            return self._redirect_to_service_flow(session, service_key)
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
            return "Vamos tentar de novo. Por favor, descreva sua necessidade para eu classificar o serviço.\n\n*(Digite 'Voltar' para o menu de serviços)*"

        self._set_state(session, session.previous_state)

        entry_message_or_func = self.state_entry_messages.get(session.state)

        if callable(entry_message_or_func):
            return entry_message_or_func(session)
        elif isinstance(entry_message_or_func, str):
            return entry_message_or_func
        else:
            session.reset()
            return self._menu_inicial(session)

    # --- Funções Auxiliares (Menus, Redirecionamento, etc.) ---

    def _redirect_to_service_flow(self, session: UserSession, service_key: str) -> str:
        """Redireciona o usuário para o início do sub-fluxo de serviço após a confirmação da IA."""
        if service_key == AccountingService.REGULARIZACAO_EMPRESA.value:
            return self._handle_service_choice_pj(session, "1")
        elif service_key == AccountingService.DEPARTAMENTO_PESSOAL.value:
            return self._handle_service_choice_pj(session, "2")
        elif service_key == AccountingService.ABERTURA_EMPRESA.value:
            return self._handle_service_choice_pj(session, "3")
        elif service_key == AccountingService.PLANEJAMENTO_PATRIMONIAL.value:
            return self._handle_service_choice_pj(session, "4")
        elif service_key == AccountingService.IMPOSTO_RENDA_PF.value:
            self._set_state(session, ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF)
            return (
                self._menu_servicos_pf(session)
                + "\n\n(Te redirecionei para o menu de Pessoa Física)"
            )
        else:
            self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return self._enviar_para_atendente_humano(
                session,
                f"IA classificou '{service_key}', mas não há fluxo de redirecionamento.",
            )

    def _handle_service_choice_pj(self, session: UserSession, user_message: str) -> str:
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
            return "Opção inválida.\n" + self._menu_servicos_pj(
                session, add_stage=False
            )

    # --- Funções de Menu (Textos) ---

    def _menu_inicial(self, session, add_stage=True):
        if add_stage:
            self._set_state(session, ConversationState.AGUARDANDO_OPCAO_INICIAL)
        return (
            "Olá! Bem-vindo(a) ao atendimento da DAS Contabilidade.\n"
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
        return (
            "Serviços disponíveis para CPF:\n\n"
            "1. Imposto de Renda Pessoa Física\n\n"
            "*(Digite o número da opção ou 'Voltar')*"
        )

    def _menu_servicos_pj(self, session, add_stage=True):
        """Menu específico para Pessoa Jurídica."""
        if add_stage:
            self._set_state(session, ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ)
        return (
            "Serviços disponíveis para CNPJ:\n\n"
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

    # --- Placeholders para Integração com Backend/DB ---

    def _validar_cpf(self, cpf: str) -> bool:
        return True

    def _validar_cnpj(self, cnpj: str) -> bool:
        return True

    def _buscar_dados_documento(self, documento: str) -> dict:
        return None

    def _enviar_para_atendente_humano(self, session: UserSession, motivo: str) -> str:
        self._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
        resumo = f"Cliente: {session.client.name or 'Novo Cliente'}, Motivo: {motivo}, Documento: {session.client.document_number or 'N/A'}"

        logging.info(f"Direcionamento para humano acionado: {resumo}")
        send_email(resumo)
        return (
            "Entendido! Já estou chamando um de nossos especialistas para falar com você.\n\n"
            f"Eles receberão o seguinte resumo: *{motivo}*\n\n"
            "Por favor, aguarde que em breve alguém entrará em contato por aqui."
        )
