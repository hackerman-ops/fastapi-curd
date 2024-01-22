# which is a part of the model-t library.


import smtplib

# async send email tools
import asyncio
import aiohttp
import aiohttp.client_exceptions
import logging


class EmailSender:
    def __init__(self, host, port, username, password, use_tls=True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.logger = logging.getLogger(__name__)

    def send_email(self, sender, recipients, subject, message):
        try:
            server = smtplib.SMTP(self.host, self.port)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.sendmail(sender, recipients, message)
            server.quit()
            self.logger.info(f"Email sent to {recipients} with subject {subject}")
        except Exception as e:
            self.logger.error(
                f"Error sending email to {recipients} with subject {subject}: {e}"
            )

    async def async_send_email(self, sender, recipients, subject, message):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"smtp://{self.host}:{self.port}",
                    auth=aiohttp.BasicAuth(self.username, self.password),
                    data=f"From: {sender}\r\nTo: {recipients}\r\nSubject: {subject}\r\n\r\n{message}",
                ) as response:
                    if response.status == 200:
                        self.logger.info(
                            f"Email sent to {recipients} with subject {subject}"
                        )
                    else:
                        self.logger.error(
                            f"Error sending email to {recipients} with subject {subject}: {response.status} {response.reason}"
                        )
        except aiohttp.client_exceptions.ClientConnectorError as e:
            self.logger.error(f"Error connecting to SMTP server: {e}")
        except Exception as e:
            self.logger.error(
                f"Error sending email to {recipients} with subject {subject}: {e}"
            )


# fastapi async send email
async def send_email(email_sender: EmailSender, sender, recipients, subject, message):
    if isinstance(recipients, str):
        recipients = [recipients]
    await email_sender.async_send_email(sender, recipients, subject, message)
