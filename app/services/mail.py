import logging
from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from app.core.config import settings
from app.schemas.mail import MailModel

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent.parent.parent / "templates" / "email",
)

class MailService:
    """
    Сервіс для відправки email-повідомлень.
    """

    async def send_email(self, mail: MailModel) -> bool:
        """
        Надіслати email.
        """
        try:
            logging.info(f"Sending email to {mail.to}")
            message = MessageSchema(
                subject=mail.subject,
                recipients=mail.to,
                template_body=mail.data,
                subtype=MessageType.html,
            )
            fm = FastMail(conf)
            await fm.send_message(message, template_name=mail.template)
            logging.info(f"Email sent to {mail.to}")
        except ConnectionErrors as err:
            logging.error(f"Error sending email: {err}")
            return False
        except Exception as err:
            logging.error(f"Error sending email: {err}")
            return False
        return True

mail_service = MailService()
