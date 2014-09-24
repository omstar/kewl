import smtplib
from email.mime.text import MIMEText as text

def send_mail(sender,receiver,subject, message, cc, bcc):
    sender = sender
    receivers = receiver
    m = text(message)
    m['Subject'] = subject
    m['From'] = sender
    m['To'] = receiver
    m['Cc'] = ','.join(cc)
    m['Bcc'] = ','.join(bcc)

   # message = message

    try:
       smtpObj = smtplib.SMTP('localhost')
       smtpObj.sendmail(sender, [receivers] + cc + bcc, str(m))
       print "Successfully sent email"
    except smtplib.SMTPException:
       print "Error: unable to send email"


send_mail("omprakash1989@gmail.com", "omprakash1989@gmail.com", "check", "%s"%message, [], [])



