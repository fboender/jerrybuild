import os
import errno
import smtplib
import getpass
import socket

def mail(to, subject, msg, smtp_server="localhost"):
    from_ = '{}@{}'.format(getpass.getuser(), socket.getfqdn())

    to_header = ', '.join(['<{}>'.format(t) for t in to])
    message = """To: <{}>
Subject: {}

{}
""".format(to_header, subject, msg)

    smtpObj = smtplib.SMTP(smtp_server)
    smtpObj.sendmail(from_, to, message)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
