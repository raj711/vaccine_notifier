import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


try:
    s = smtplib.SMTP(os.environ.get("SMTP_HOST"), int(os.environ.get("SMTP_PORT")))

    s.starttls()
    s.login(os.environ.get("SENDER_EMAIL"), os.environ.get("SENDER_EMAIL_PASSWORD"))
except Exception as e:
    print("Something wrong...", str(e))
    s = None


def send_email(reciever_email, data):
    try:
        sender_email = os.environ.get("SENDER_EMAIL")
        receiver_email = reciever_email
        sub = "Vaccine Notification"
        message = MIMEMultipart("alternative")
        message["Subject"] = sub
        message["From"] = sender_email
        message["To"] = receiver_email

        html = """\
        <html>
          <body>
            <p>Hi,<br>
               Available slots for booking are as below: <br>
            </p>
            <p>
                {data}
            </p>
          </body>
        </html>
        """.format(data=data)

        html_msg = MIMEText(html, "html")
        message.attach(html_msg)
        s.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print("Something wrong in sending email...", str(e))
        return False