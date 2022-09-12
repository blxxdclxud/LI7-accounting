import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import mimetypes

from dotenv import load_dotenv


async def send_email(email, subject, text, attachments, server=None):
    load_dotenv()

    _from = os.getenv("FROM")

    msg = MIMEMultipart()
    msg['From'] = _from
    print(_from)
    msg['To'] = email
    msg['Subject'] = subject

    msg.attach(MIMEText(text, 'plain'))

    ftype, _ = mimetypes.guess_type(attachments)
    file_type, subtype = ftype.split("/")

    if file_type == "application":
        with open(attachments, 'rb') as f:
            file = MIMEApplication(f.read(), subtype)

    file.add_header('content-disposition', 'attachment', filename="Квитанция")
    msg.attach(file)

    # print(_from, host, port)
    # st = time.time()
    await server.send_message(msg)
    # et = time.time()
    # print(et - st)
