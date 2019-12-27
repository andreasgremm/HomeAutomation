#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
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
usetls = True


########################################
# function to send a mail              #
########################################
def sendmail(recipient, subject, content):

    # generate a RFC 2822 message
    # 	msg = MIMEText(content)
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    part1 = MIMEText(content[0], "plain")
    part2 = MIMEText(content[1], "html")
    msg.attach(part1)
    msg.attach(part2)

    # open SMTP connection
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
