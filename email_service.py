import json
from flask import render_template
import os
import smtplib
from smtplib import SMTPServerDisconnected
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback


class EmailService:
    def __init__(self):
        self.smtp = None

    def connect(self):
        try:
            self.smtp = smtplib.SMTP(os.environ.get("SMTP_HOST"), int(os.environ.get("SMTP_PORT")))

            self.smtp.starttls()
            self.smtp.login(os.environ.get("SENDER_EMAIL"), os.environ.get("SENDER_EMAIL_PASSWORD"))
        except Exception as e:
            print("Something wrong...", str(e))
            self.smtp = None

    def send_email(self, reciever_email, data, district, age, app):
        try:
            app.logger.info("Send Email to {}".format(reciever_email))
            sender_email = os.environ.get("SENDER_EMAIL")
            receiver_email = reciever_email
            sub = "Vaccine Notification"
            message = MIMEMultipart("alternative")
            message["Subject"] = sub
            message["From"] = f"Vaccine Notifier{sender_email}"
            message["To"] = receiver_email

            with app.app_context():
                html = render_template('main.html', district_name=district, data=data)

            html_msg = MIMEText(html, "html")
            message.attach(html_msg)
            self.smtp.sendmail(sender_email, receiver_email, message.as_string())
            return True
        except SMTPServerDisconnected as ex:
            app.logger.error("Connected again..")
            self.connect()
            self.send_email(reciever_email, data, district, age, app)
        except Exception as e:
            app.logger.error("Something wrong in sending email...", str(e))
            # app.logger.info(str(traceback.print_exc()))
            return False