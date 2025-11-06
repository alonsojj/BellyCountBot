# importações
import smtplib
from email.message import EmailMessage


from app.core.settings import get_settings


def send_email(resumo):
    settings = get_settings()
    remetente = settings.EMAIL_SENDER_ADDRESS
    destinatario = (
        settings.EMAIL_SENDER_ADDRESS
    )  # Enviando para o mesmo e-mail por enquanto
    assunto = "Clientes em contato"
    mensagem = f"""
    Olá,
    Um cliente entrou em contato via bot, aqui estão as informações para seguirem com o atendimento personalizado:
    {resumo}
    Att,
    """

    senha = settings.EMAIL_SENDER_PASSWORD

    # Criar o E-mail
    msg = EmailMessage()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content(mensagem)

    # Realizar o envio do e-mail
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(remetente, senha)
        smtp.send_message(msg)

        print("E-mail enviado com sucesso")
