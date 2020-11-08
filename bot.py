import poplib
from email.parser import Parser
from unidecode import unidecode
from params import *

server = poplib.POP3_SSL(mailserver, port)
server.user(user)
server.pass_(pw)

resp, mails, octets = server.list()
index = len(mails)
resp, lines, octets = server.retr(index)

server.quit()

trunc = []
flag = False
for line in lines:
    if line.startswith(b'On '):
        flag = True
        trunc.append(line)
    elif flag:
        if line.startswith(b'> '):
            trunc.append(b'(Quoted message hidden)')
            break
    else:
        trunc.append(line)

msg_content = b'\n'.join(trunc).decode('utf-8')
msg = Parser().parsestr(msg_content)

relay = "NEW EMAIL\n\n"

email_from = msg.get('From')
email_to = msg.get('To')
email_cc = msg.get('Cc')
email_subject = msg.get('Subject')

if email_from:
    relay += 'From: ' + email_from + '\n'
if email_to:
    relay += 'To: ' + email_to + '\n'
if email_cc:
    relay += 'Cc: ' + email_cc + '\n'
if email_subject:
    relay += 'Subject: ' + email_subject + '\n'
relay += '\n'

if msg.is_multipart():
    for part in msg.walk():
        ctype = part.get_content_type()
        cdispo = str(part.get('Content-Disposition'))
        if ctype == 'text/plain' and 'attachment' not in cdispo:
            body = part.get_payload(decode=True)
            break
else:
    body = msg.get_payload(decode=True)

relay += unidecode(body.decode("utf-8")).strip()
