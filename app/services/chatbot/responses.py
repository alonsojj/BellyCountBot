# app/services/chatbot/responses.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_session import UserSession


def menu_inicial(session: "UserSession") -> str:
    """Gera a mensagem de saudação e o menu inicial."""
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
        "*(Digite o número da opção desejada ou em poucas palavras o que deseja)*"
    )


def menu_servicos_pf(session: "UserSession") -> str:
    """Gera o menu de serviços para Pessoa Física."""
    greeting = ""
    if session.client.name:
        greeting = f"Olá, {session.client.name}! "
    return (
        f"{greeting}Serviços disponíveis para CPF:\n\n"
        "1. Imposto de Renda Pessoa Física\n\n"
        "*(Digite o número da opção ou 'Voltar')*"
    )


def menu_servicos_pj(session: "UserSession") -> str:
    """Gera o menu de serviços para Pessoa Jurídica."""
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


def menu_planejamento(session: "UserSession") -> str:
    """Gera o menu para a área de Planejamento."""
    return (
        "Qual o seu objetivo com o Planejamento?\n\n"
        "1. Reduzir legalmente a carga tributária\n"
        "2. Reestruturar seu regime de tributação\n"
        "3. Obter consultoria preventiva\n"
        "4. Revisar tributos pagos nos últimos anos\n\n"
        "*(Digite o número da opção ou 'Voltar')*"
    )
