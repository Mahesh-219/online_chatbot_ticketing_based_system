import smtplib
from email.mime.text import MIMEText

sender = "dhanu.innovation@gmail.com"
password = "cxvb yglu bvtn vcer"

def send_email(data,monthname):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       for temp in data:
            body="Dear " + temp['FirstName'] +" " + temp['LastName'] +\
                 " your salary of " + temp['Salary'] + " for month "+ monthname +\
                 " got credited to your account " + \
                 temp['BankName'] + " AccountNumber : " + temp['AccountNumber']
            subject = "Salary got credited for "+monthname+" month"
            toemail = temp['EmailId']
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = toemail
            smtp_server.sendmail(sender, toemail, msg.as_string())
    print("Message sent!")