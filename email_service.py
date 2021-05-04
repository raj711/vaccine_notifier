import json
from flask import render_template
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback


try:
    s = smtplib.SMTP(os.environ.get("SMTP_HOST"), int(os.environ.get("SMTP_PORT")))

    s.starttls()
    s.login(os.environ.get("SENDER_EMAIL"), os.environ.get("SENDER_EMAIL_PASSWORD"))
except Exception as e:
    print("Something wrong...", str(e))
    s = None


def send_email(reciever_email, data, district, age, app):
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
            html = render_template('main.html', res=data)

        # html = """\
        # <html>
        #   <body>
        #     <p>Hi,<br>
        #        Available slots for booking are as below: <br>
        #     </p>
        #     <p>
        #         {data}
        #     </p>
        #   </body>
        # </html>
        # """.format(data=data)

        html_msg = MIMEText(html, "html")
        message.attach(html_msg)
        s.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        app.logger.error("Something wrong in sending email...", str(e))
        # app.logger.info(str(traceback.print_exc()))
        return False