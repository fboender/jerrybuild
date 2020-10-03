# Running directly from repo

You can run Jerrybuild directly from a git clone of the repository:

    $ git clone git@github.com:fboender/jerrybuild.git
    $ cd jerrybuild/
    $ python3 ./jerrybuild.py example/jerrybuild.cfg

This is mostly useful for evaluating Jerrybuild. If you're satisfied that
Jerrybuild suits your needs, you should do a real install.

# Pip

If Pip (the Python package manager) is available on your system, you can
install Jerrybuild using Pip. This requires Python v3.

See the [Python Packaging User
Guide](https://packaging.python.org/guides/installing-using-linux-tools/#installing-pip-setuptools-wheel-with-linux-package-managers)
for information on how to install Pip on your OS.

You can install Jerrybuild system-wide:

    $ sudo pip install jerrybuild

Or you can install it in your home dir's `~/.local/` dir:

    $ pip install jerrybuild

Jerrybuild can also be installed to any Python virtualenv:

    $ /opt/pythonenv/bin/pip install jerrybuild

# Stand-alone binary

A stand-alone binary is offered that doesn't require you to have Python
installed at all. You can get the binary from the [Github Releases
page](https://github.com/fboender/jerrybuild/releases/). Search for a
`jerrybuild-X.Y-bin64.tar.gz` file.

