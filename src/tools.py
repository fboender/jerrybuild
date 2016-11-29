import os
import sys
import errno
import smtplib
import getpass
import socket
from datetime import datetime, timedelta
import re
import glob
import stat
if sys.version_info.major > 2:
    import configparser as ConfigParser
    from io import StringIO as StringIO
else:
    import ConfigParser
    from StringIO import StringIO

def bin_rel_path(path):
    """
    Return the full real path to `path`, where `path` is relative to the binary
    currently running.
    """
    return os.path.join(
        os.path.dirname(
            os.path.realpath(
                sys.argv[0]
            )
        ),
        path
    )

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

def config_load(path, case_sensitive=True):
    """
    ConfigParser wrapper with support for includes.

    To include files, put the following in your config on separate line:

        %include conf.d/*.conf

    Files starting with 'EXAMPLE' will not be included

    """
    base_path = os.path.dirname(os.path.realpath(path))

    with open(path, 'r') as base_fp:
        base_cfg = base_fp.read()

    for match in re.findall('^%include (.*)$', base_cfg, flags=re.MULTILINE):
        files = glob.glob(os.path.join(base_path, match))
        if not files:
            raise RuntimeError("No config files found for include '{}'".format(os.path.join(base_path, match)))

        include_cfg = ""
        for file in files:
            if os.path.basename(file).startswith('EXAMPLE'):
                continue
            include_cfg += open(os.path.join(base_path, file), 'r').read()
        include_stmt = '^%include {}$'.format(re.escape(match))
        base_cfg = re.sub(include_stmt, include_cfg, base_cfg, flags=re.MULTILINE)

    config_fp = StringIO(base_cfg)
    conf = ConfigParser.ConfigParser()
    if not case_sensitive:
        conf.optionxform = str
    conf.readfp(config_fp)

    return conf

def listdir_sorted(path, stat_key='st_mtime', reverse=False):
    """
    Return a list of file / dir names in `path`, sorted by `stat_key`. If
    `reverse` is True, the result is reverse (biggest/oldest first).

    `stat_key` must be a string contaiing a valid field of the os.stat()
    structure.. i.e: 'st_size', 'st_mtime', 'st_ctime' or 'st_atime'.

    OSError Errno 2 (No such file or directory) errors are ignored. These are
    caused by invalid symlinks.
    """
    files = []
    for fname in os.listdir(path):
        try:
            fstat = os.stat(os.path.join(path, fname))
            files.append((getattr(fstat, stat_key), fname))
        except OSError as err:
            if err.errno == 2:
                pass
            else:
                raise

    return [fname for fprop, fname in sorted(files, reverse=reverse)]

def to_bool(s):
    """
    Convert string `s` into a boolean. `s` can be 'true', 'True', 1, 'false',
    'False', 0.

    Examples:

    >>> to_bool("true")
    True
    >>> to_bool("0")
    False
    >>> to_bool(True)
    True
    """
    if isinstance(s, bool):
        return s
    elif s.lower() in ['true', '1']:
        return True
    elif s.lower() in ['false', '0']:
        return False
    else:
        raise ValueError("Can't cast '%s' to bool" % (s))

if __name__ == '__main__':
   import doctest
   doctest.testmod()
