import os
import smtplib

from email.message import EmailMessage


class EmailService:

    def __init__(self):

        self.smtp_host = os.getenv(
            "SMTP_HOST",
            "smtp.gmail.com"
        )

        self.smtp_port = int(
            os.getenv(
                "SMTP_PORT",
                "587"
            )
        )

        self.smtp_username = os.getenv(
            "SMTP_USERNAME"
        )

        self.smtp_password = os.getenv(
            "SMTP_PASSWORD"
        )

        self.developer_email = os.getenv(
            "DEVELOPER_EMAIL"
        )

        self.from_email = os.getenv("FROM_EMAIL")

    def send_restart_alert(
        self,
        container_name: str,
        restart_count: int
    ):

        if not all([
            self.smtp_username,
            self.smtp_password,
            self.developer_email,
        ]):
            print(
                "[EMAIL] SMTP configuration is missing",
                flush=True
            )
            return

        message = EmailMessage()

        message["Subject"] = (
            f"ALERT: Container {container_name} "
            f"restarted {restart_count} times"
        )

        message["From"] = self.from_email

        message["To"] = self.developer_email

        message.set_content(
            f"""
Docker Container Restart Alert

Container:
{container_name}

Restart count:
{restart_count}

The monitoring service detected that this container
has restarted 3 or more times.

Please investigate the container logs.
"""
        )

        try:

            with smtplib.SMTP(
                self.smtp_host,
                self.smtp_port
            ) as server:

                server.starttls()

                server.login(
                    self.smtp_username,
                    self.smtp_password
                )

                server.send_message(message)

            print(
                f"[EMAIL] Alert sent for {container_name}",
                flush=True
            )

        except Exception as error:

            print(
                f"[EMAIL ERROR] {error}",
                flush=True
            )