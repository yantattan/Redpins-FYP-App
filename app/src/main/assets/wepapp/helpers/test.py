import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

mailFrom = "redpinsbuffer@gmail.com"
mailTo = "yantattan721@gmail.com"
msg = MIMEMultipart()
msg['Subject'] = "Change of password"
msg['From'] = mailFrom
msg['To'] = mailTo
emailBody = '<div class="container text-center">' \
            '<h1>Redpins Buffer</h1>' \
            '<p>Your password has been reset:</p>' \
            '<p><b>{}</b></p>' \
            '</div>'.format("Gayman")

msg.attach(MIMEText(emailBody, "html"))

mail = smtplib.SMTP('smtp.gmail.com', 587)
mail.ehlo
mail.starttls()
mail.login('redpinsbuffer@gmail.com', 'redpinsP@ssw0rd')
mail.sendmail(mailFrom, mailTo, msg.as_string())
mail.quit()