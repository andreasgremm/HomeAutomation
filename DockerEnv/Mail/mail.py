#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Security.Mail import sender, smtpserver, smtpusername, smtppassword

########################################
# declaration of default mail settings #
########################################
###
#
# Provide the following values
# sender = <Email Adresse Sender>
# smtpserver = <FQDN des SMTP Servers>:<Port>
# smtpusername = <Username für SMTP Authentication>
# smtppassword = <Passwort für SMTP Authentication>

# use TLS encryption for the connection


########################################
# function to send a mail              #
########################################
def sendmail(
    recipient,
    subject,
    content,
    sender=sender,
    smtpserver=smtpserver,
    smtpusername=smtpusername,
    smtppassword=smtppassword,
    usetls=True,
    usessl=False,
    multipart="alternative",
    multicontent=["plain", "html"],
    filename="noname.pdf"
):

    # generate a RFC 2822 message
    # 	msg = MIMEText(content)
    msg = MIMEMultipart(multipart)
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    part1 = MIMEText(content[0], multicontent[0])
    if multicontent[1] == "html":
        part2 = MIMEText(content[1], multicontent[1])
    elif multicontent[1] == "pdf":
        part2 = MIMEApplication(content[1], _subtype=multicontent[1])
        part2.add_header('content-disposition', 'attachment',
                         filename=filename)
    msg.attach(part1)
    msg.attach(part2)

    # open SMTP connection
    if usessl:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(smtpserver, context=context)
    else:
        server = smtplib.SMTP(smtpserver)

    # start TLS encryption
    if usetls:
        server.starttls()

    # login with specified account
    if smtpusername and smtppassword:
        server.login(smtpusername, smtppassword)

    # send generated message
    server.sendmail(sender, recipient, msg.as_string())

    # close SMTP connection
    server.quit()
