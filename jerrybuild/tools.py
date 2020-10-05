import os
import sys
import errno
import smtplib
import getpass
import socket
import re
import glob
import logging
import configparser as ConfigParser
from io import StringIO as StringIO


# Timeunit mapping for duration()
timeunit_map = [
    ("y", 60 * 60 * 24 * 365),
    # months is a special case and calculated in duration()
    ("w", 60 * 60 * 24 * 7),
    ("d", 60 * 60 * 24),
    ("h", 60 * 60),
    ("m", 60),
    ("s", 1),
]

log = logging.getLogger(__name__)


def data_path(path=None):
    """
    Return the location where data files are stored. This works both when
    running the program from source (e.g. a git clone), when running from an
    installed bdist wheel (system, local or virtualenv) and when running from a
    pyinstaller-generated binary.

    For bdist wheels, data files are specified in `setup.py` `data_files`.

    You can specify an optional `path` to reference files inside the data dir
    directly. If `path` is not specified, it just returns the path to the data
    directory itself.
    """
    # pylint: disable=protected-access
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller binary bundle
        dir_name = os.path.dirname(os.path.realpath(sys.executable))
        rel_path = os.path.join(dir_name, "..", "lib", __package__)
        data_dir = os.path.realpath(rel_path)
    elif __file__.startswith(sys.prefix):
        # Running from bdist installed wheel
        data_dir = os.path.join(sys.prefix, 'lib', __package__)
    else:
        # Running from the git repo
        dir_name = os.path.dirname(os.path.realpath(sys.argv[0]))
        rel_path = os.path.join(dir_name, "data")
        data_dir = os.path.realpath(rel_path)

    if path is not None:
        return os.path.join(data_dir, path)
    else:
        return data_dir


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

    >>> minutes = 60
    >>> hours = minutes * 60
    >>> days = hours * 24
    >>> weeks = days * 7
    >>> years = days * 365

    >>> duration(12)
    '12s'
    >>> duration(minutes * 2 + 5)
    '2m 5s'
    >>> duration(hours * 3 + 125)
    '3h 2m'
    >>> duration((days * 2) + (hours * 4))
    '2d 4h'
    >>> duration((days * 9))
    '1w 2d'
    >>> duration((days * 28))
    '1mo'
    >>> duration((days * 30))
    '1mo'
    >>> duration((days * 31))
    '1mo'
    >>> duration((days * 50))
    '2mo'
    >>> duration((days * 60))
    '2mo'
    >>> duration((days * 180))
    '6mo'
    >>> duration((years * 1) + (days * 5))
    '1y'
    >>> duration((years * 1) + (days * 28))
    '1y 1mo'
    >>> duration((years * 1) + (days * 50))
    '1y 2mo'
    >>> duration((years * 3) + (days * 60))
    '3y 2mo'
    """
    res = []
    rest = secs
    for tu_symbol, tu_duration in timeunit_map:
        nr_of_timeunits = rest / tu_duration
        rest = rest % tu_duration

        if int(nr_of_timeunits) > 0:
            if tu_symbol == 'w' and nr_of_timeunits > 3:
                # Special case for months.
                res.append("{}mo".format(int(round(nr_of_timeunits / 4.0))))
                break
            else:
                res.append("{}{}".format(int(nr_of_timeunits), tu_symbol))

            if tu_symbol == 'y' and rest < (60 * 60 * 24 * 28):
                break

        if len(res) == 2:
            break

    return " ".join(res)


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
            log.warning("No config files found for include '{}'".format(os.path.join(base_path, match)))

        include_cfg = ""
        for file in files:
            if os.path.basename(file).startswith('EXAMPLE'):
                continue
            path = os.path.join(base_path, file)
            log.info("Loading {}".format(path))
            include_cfg += open(path, 'r').read()
        include_stmt = '^%include {}$'.format(re.escape(match))
        base_cfg = re.sub(include_stmt, include_cfg, base_cfg, flags=re.MULTILINE)

    config_fp = StringIO(base_cfg)
    conf = ConfigParser.ConfigParser()
    if not case_sensitive:
        conf.optionxform = str
    conf.read_file(config_fp)

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
