#! /usr/bin/env /usr/bin/python3
from email.message import EmailMessage
from smtplib import SMTP
import os
import socket
from .templates.reset_mail import send_resetmail
from .templates.send_verification import send_verification
from .templates.send_share import send_share
from .templates.send_notification import send_noti

def mail(payload=None):
    try:
        host = os.environ.get("MAIL_SERVER")
        user = os.environ.get("MAIL_USER")
        port = os.environ.get("MAIL_PORT")
        password = os.environ.get("MAIL_PASSWORD")
        encryption = os.environ.get("MAIL_ENCRYPTIONPROTOCOL")

        if not host:
            return [ False, 404, "Mailconfig not found" ]
    except:
        return [ False, 404, "Mailconfig not found" ]


    try:
        domain = os.environ.get("DOMAIN")
    except:
        hostname = socket.gethostname()
        domain = socket.gethostbyname(hostname)

    to_address = payload["to_address"]
    mode = payload["mode"] 

    if mode == "reset":
        hashed_url = payload["hashed_url"]
        html, subject = send_resetmail(hashed_url,domain)
    elif mode == "verify":
        hashed_url = payload["hashed_url"]
        html, subject = send_verification(hashed_url,domain)
    elif mode == "share":
        hashed_url = payload["hashed_url"]
        mail_user = payload["user"]
        budget = payload["budget"]
        html, subject = send_share(mail_user,budget,hashed_url,domain)

        if not html:
            return [ False, 502, "HTML building error" ]

    elif mode == "noti":
        value = payload["value"]
        header = payload["header"]
        html, subject = send_noti(to_address,value,header,domain)
    else:
        print("[ERROR] Creating email",flush=True)


    msg = EmailMessage()
    msg['Subject'] = subject
    msg['To'] = to_address
    msg['From'] = user
    msg.set_content(html, subtype='html')

    try:
        s = SMTP(host, int(port))
        if encryption == "STARTTLS":
            s.starttls()
        s.login(user, password)
        s.send_message(msg)
        s.quit()

        return [ True, 200, "OK" ] 
    #except SMTPResponseException as e:
    #    return [ False, e.smtp_code, e.smtp_error ]
    except:
        return [ False, "Mail", "error" ]
