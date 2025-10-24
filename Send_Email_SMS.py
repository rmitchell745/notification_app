import smtplib
from email.mime.text import MIMEText
from Logger import logger

# define an email config class
class EmailConfig:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(EmailConfig, cls).__new__(cls)
            logger.info("EmailConfig singleton instance created.")
        return cls.__instance

    def __init__(self, config):
        if not hasattr(self, '_initialized'):

            if config and 'smtp_server' in config and 'smtp_port' in config and 'sender_email' in config and 'sender_password' in config:
                self.smtp_server = config['smtp_server']
                self.smtp_port = config['smtp_port']
                self.sender_email = config['sender_email']
                self.sender_password = config['sender_password']
                self._initialized = True
                logger.info("EmailConfig instance initialized successfully.")
            else:
                logger.error("Missing required email configuration keys in config.")

                self._initialized = False


    @classmethod
    def get_instance(cls, config=None):
        if cls.__instance is None:
            if config is None:
                logger.error("Config must be provided on first initialization of EmailConfig.")
                raise ValueError("Config must be provided on first initialization")
            cls.__instance = cls(config)
        return cls.__instance




# send the email function
def send_email(ssl_context, sender_email, ph_nmbr, carrier, subject, body, carrier_sms_protocol):
    carrier_domain = carrier_sms_protocol.get(carrier)
    if not carrier_domain:
        logger.warning(f"Unknown carrier '{carrier}'. Cannot send SMS to {ph_nmbr}.")
        return

    receiver_email = f"{ph_nmbr}@{carrier_domain}" # Added @
    message = f"Subject: {subject}\n\n{body}" # Use f-string for subject and body

    try:
        ssl_context.sendmail(sender_email, receiver_email, message)
        logger.info(f"Email sent successfully to {receiver_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {receiver_email}: {e}")
