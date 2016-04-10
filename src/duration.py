# Copyright (c) 2010 Ferry Boender
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

__VERSION__ = (0, 1)

from datetime import datetime, timedelta

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
