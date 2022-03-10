from flask_mail import Message

from notify import mail, rq


@rq.job(description='send message', func_or_queue='campus_notify_default')
def send_notification(info: str, message: str, email_address: str):
    msg = Message(info, recipients=[email_address])
    msg.html = message
    mail.send(msg)
    return
