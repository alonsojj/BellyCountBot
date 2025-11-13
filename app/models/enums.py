from enum import Enum, auto


class ConversationState(Enum):
    # --- Estágios Iniciais ---
    GREETING = auto()  # Estado inicial (primeira mensagem)
    AGUARDANDO_OPCAO_INICIAL = auto()  # Mostrou o menu (1, 2, 3) e está esperando

    # --- Fluxo 2: Serviços ---
    AGUARDANDO_CPF_CNPJ = auto()  # Esperando o CPF/CNPJ
    AGUARDANDO_NOME_PF = auto()
    AGUARDANDO_ESCOLHA_SERVICO_PF = auto()  # Menu de Pessoa Física (CPF)
    AGUARDANDO_ESCOLHA_SERVICO_PJ = auto()  # Menu de Pessoa Jurídica (CNPJ)

    # --- Fluxo 2 (Sub-Estágios de Serviços PJ) ---
    SERVICO_DEPTO_PESSOAL_PERGUNTA_1 = auto()  # "Já possui funcionários?"
    SERVICO_ABERTURA_EMPRESA_PERGUNTA_1 = auto()  # "Já definiu o tipo?"
    SERVICO_PLANEJAMENTO_MENU = auto()  # Mostrou o menu de Planejamento (1, 2, 3, 4)

    # Estados para o fluxo "Outro" (IA)
    SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION = auto()  # Esperando descrição para a IA
    SERVICO_IA_CLASSIFY_AWAIT_CONFIRMATION = (
        auto()
    )  # Esperando Sim/Não para a sugestão da IA

    # --- Fluxo 3: Dúvidas (IA) ---
    DOUBTS = auto()  # Usuário está em um loop de conversa com a IA
    AI_CLASSIFICATION_FALLBACK = auto()  # AI tentando classificar input não reconhecido

    # --- Estágios Finais ---
    ATENDIMENTO_HUMANO = auto()  # Estágio final. O bot para de responder.
    HUMAN_ATTENDING = auto()  # Um humano está ativamente conversando com o cliente.


# Enum completo com todos os serviços do fluxograma
class AccountingService(Enum):
    REGULARIZACAO_EMPRESA = "REGULARIZACAO_EMPRESA"
    IMPOSTO_RENDA_PF = "IMPOSTO_RENDA_PF"
    DEPARTAMENTO_PESSOAL = "DEPARTAMENTO_PESSOAL"
    ABERTURA_EMPRESA = "ABERTURA_EMPRESA"
    PLANEJAMENTO_PATRIMONIAL = "PLANEJAMENTO_PATRIMONIAL"  # Categoria principal
    PLANEJAMENTO_REDUZIR_CARGA = "PLANEJAMENTO_REDUZIR_CARGA"
    PLANEJAMENTO_REESTRUTURAR_REGIME = "PLANEJAMENTO_REESTRUTURAR_REGIME"
    PLANEJAMENTO_CONSULTORIA_PREVENTIVA = "PLANEJAMENTO_CONSULTORIA_PREVENTIVA"
    PLANEJAMENTO_REVISAR_TRIBUTOS = "PLANEJAMENTO_REVISAR_TRIBUTOS"
    OUTRO = "OUTRO"  # Fallback da IA


class DocumentType(Enum):
    CPF = "CPF"
    CNPJ = "CNPJ"


class AccessOption(str, Enum):
    WHITELIST = "WHITELIST"
    BLACKLIST = "BLACKLIST"
    DISABLE = "DISABLE"
