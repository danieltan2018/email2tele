import telegram
import schedule
import time
import poplib
from email.parser import Parser
from unidecode import unidecode
import re
from params import *


bot = telegram.Bot(token=bottoken)
latest = 0


def process(lines):
    trunc = []
    flag = False
    for line in lines:
        if line.startswith(b'> '):
            trunc.append(b'[Quoted message hidden]')
            break
        trunc.append(line)

    msg_content = b'\n'.join(trunc).decode('utf-8')
    msg = Parser().parsestr(msg_content)

    relay = ""

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

    relay = re.sub('\n(?=\w)', ' ', relay)

    relay = relay.replace('\n', '\n\n')

    while ' \n' in relay:
        relay = relay.replace(' \n', '\n')

    while '\n\n\n' in relay:
        relay = relay.replace('\n\n\n', '\n\n')

    return relay


def send(mail):
    n = 4000
    out = [(mail[i:i+n]) for i in range(0, len(mail), n)]
    for mail in out:
        bot.send_message(chat_id=group, text=mail,
                         disable_web_page_preview=True)


def getmail():
    server = poplib.POP3_SSL(mailserver, port)
    server.user(user)
    server.pass_(pw)
    resp, mails, octets = server.list()
    index = len(mails)
    index = 91
    resp, lines, octets = server.retr(index)
    server.quit()

    global latest
    if index != latest:
        latest = index
        mail = process(lines)
        send(mail)


def main():
    send('Connecting to {} mail server...'.format(user))
    getmail()
    schedule.every(5).to(10).minutes.do(getmail)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == '__main__':
    main()
