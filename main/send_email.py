from pandas import DataFrame as df
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import smtplib
import datetime
import webbrowser


def using_google(data, total_seconds_worked):
    # me == my email address
    # you == recipient's email address
    me = "shashwat221@gmail.com"
    you = "shashwat221@gmail.com"

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Hours for last week"
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).
    text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = "<html><head></head><body>" + data.to_html() + "<br><b> Total hours: " + str(total_seconds_worked) + "</b></body></html>"

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login('shashwat221@gmail.com', 'adsbshiflcpiikfm')
    mail.sendmail(me, you, msg.as_string())
    mail.quit()