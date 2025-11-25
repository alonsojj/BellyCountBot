# importações
import smtplib
from email.message import EmailMessage
from email.mime.image import MIMEImage
from app.core.settings import get_settings


def create_template(resumo: dict) -> str:
    with open("app/models/email/notification.html", "r", encoding="utf-8") as f:
        template = f.read()

    template = template.replace("{cliente_nome}", resumo.get("cliente_nome", ""))
    template = template.replace("{cliente_email}", resumo.get("cliente_email", ""))
    template = template.replace(
        "{cliente_telefone}", resumo.get("cliente_telefone", "")
    )
    template = template.replace("{servico_nome}", resumo.get("servico_nome", ""))
    template = template.replace(
        "{cliente_mensagem}", resumo.get("cliente_mensagem", "")
    )
    template = template.replace("{whatsapp_link}", resumo.get("whatsapp_link", ""))

    return template


def send_email(resumo):
    settings = get_settings()
    remetente = settings.EMAIL_SENDER_ADDRESS
    destinatario = (
        settings.EMAIL_SENDER_ADDRESS
    )  # Enviando para o mesmo e-mail por enquanto

    senha = settings.EMAIL_SENDER_PASSWORD

    # Criar o E-mail
    msg = EmailMessage()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = "Novo Contato de Cliente"
    html_content = create_template(resumo)
    msg.add_alternative(html_content, subtype="html")

    # Embed the logo
    with open("images/logo.png", "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", "<logo>")
    msg.attach(logo)

    # Realizar o envio do e-mail
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(remetente, senha)
        smtp.send_message(msg)

        print("E-mail enviado com sucesso")
