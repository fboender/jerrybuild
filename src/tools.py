import os
import errno
import smtplib
import getpass
import socket
from datetime import datetime, timedelta


def mail(to, subject, msg, smtp_server="localhost"):
    """
    Email sender helper.
    """
    from_ = '{}@{}'.format(getpass.getuser(), socket.getfqdn())

    to_header = ', '.join(['<{}>'.format(t) for t in to])
    message = """To: <{}>
Subject: {}

{}
""".format(to_header, subject, msg)

    smtpObj = smtplib.SMTP(smtp_server)
    smtpObj.sendmail(from_, to, message)

def mkdir_p(path):
    """Create directories and their parent directories if required. (mkdir -p).
    Unlike os.makedirs, this doesn't raise an exception if the path already
    exists."""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def duration(secs):
    """
    Return a human-readable representation of elapsed time.

    Examples:

    >>> duration(0)
    '0s'
    >>> duration(4)
    '4s'
    >>> duration(456)
    '7m 36s'
    >>> duration(4567)
    '1h 16m'
    >>> duration(45678)
    '12h 41m'
    >>> duration(456789)
    '5d 6h'
    >>> duration(3456789)
    '9d 13m'
    >>> duration(23456789)
    '28d 11h'
    """

    sec = timedelta(seconds=int(secs))
    d = datetime(1,1,1) + sec
    k = ["%dd", "%dh", "%dm", "%ds"]
    v = [d.day-1, d.hour, d.minute, d.second]
    t = [k[i] % (v[i]) for i in range(len(k)) if v[i] > 0]
    if not t:
        return '0s'
    else:
        return ' '.join(t[:2])

if __name__ == '__main__':
   import doctest
   doctest.testmod()
