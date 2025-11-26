import logging
import smtplib
from email.message import EmailMessage
from email.mime.image import MIMEImage
from app.core.settings import Settings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings
        logging.info("EmailService inicializado.")

    def _create_template(self, resumo: dict) -> str:
        try:
            with open("app/models/email/notification.html", "r", encoding="utf-8") as f:
                template = f.read()

            template = template.replace(
                "{cliente_nome}", resumo.get("cliente_nome", "Cliente")
            )
            template = template.replace(
                "{cliente_email}", resumo.get("cliente_email", "Não Informado")
            )
            template = template.replace(
                "{cliente_telefone}", resumo.get("cliente_telefone", "Não Informado")
            )
            template = template.replace(
                "{servico_nome}", resumo.get("servico_nome", "Não Especificado")
            )
            template = template.replace(
                "{cliente_mensagem}", resumo.get("cliente_mensagem", "Sem mensagem")
            )
            template = template.replace(
                "{whatsapp_link}", resumo.get("whatsapp_link", "#")
            )

            return template
        except FileNotFoundError:
            logging.error(
                "Erro: Template de e-mail 'notification.html' não encontrado."
            )
            return "Erro ao carregar template de e-mail."
        except Exception as e:
            logging.error(f"Erro ao criar template de e-mail: {e}")
            return "Erro ao criar template de e-mail."

    def send_notification_email(self, resumo: dict, recipient_email: str):
        remetente = self.settings.EMAIL_SENDER_ADDRESS
        senha = self.settings.EMAIL_SENDER_PASSWORD
        smtp_server = self.settings.EMAIL_SMTP_SERVER
        smtp_port = self.settings.EMAIL_SMTP_PORT

        msg = EmailMessage()
        msg["From"] = remetente
        msg["To"] = recipient_email
        msg["Subject"] = "Novo Contato de Cliente (BellyCountBot)"
        html_content = self._create_template(resumo)
        msg.add_alternative(html_content, subtype="html")

        try:
            with open("images/logo.png", "rb") as f:
                logo_data = f.read()
            logo = MIMEImage(logo_data)
            logo.add_header("Content-ID", "<logo>")
            msg.attach(logo)
        except FileNotFoundError:
            logging.warning("Logo.png não encontrado. Enviando e-mail sem logo.")
        except Exception as e:
            logging.error(f"Erro ao anexar logo ao e-mail: {e}")

        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(remetente, senha)
                smtp.send_message(msg)
                logging.info(
                    f"E-mail de notificação enviado com sucesso para {recipient_email}"
                )
        except smtplib.SMTPAuthenticationError:
            logging.error("Erro de autenticação SMTP. Verifique o remetente e a senha.")
            raise
        except smtplib.SMTPServerDisconnected:
            logging.error("Servidor SMTP desconectado inesperadamente.")
            raise
        except smtplib.SMTPConnectError:
            logging.error(
                f"Erro de conexão SMTP. Verifique o servidor {smtp_server}:{smtp_port} e sua conexão de rede."
            )
            raise
        except Exception as e:
            logging.error(f"Erro inesperado ao enviar e-mail: {e}")
            raise
