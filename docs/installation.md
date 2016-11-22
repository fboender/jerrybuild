Jerrybuild is packaged for various Operating Systems:

* Debian / Ubuntu
* Redhat / CentOS
* Manual install

# Requirements

Jerrybuild requires:

* Python v2.7+ / v3+ (Available by default on nearly every Linux distribution)

# Running directly from repo

You can run Jerrybuild directly from a git clone of the repository:

    git clone git@github.com:fboender/jerrybuild.git
    cd jerrybuild/src
    ./jerrybuild ../contrib/jerrybuild.cfg

This is mostly useful for evaluating Jerrybuild. If you're satisfied that
Jerrybuild suits your needs, you should do a real install.

# Pip

If Pip (the Python package manager) is available on your system, you can
install Jerrybuild using Pip:

    pip install jerrybuild

# Debian / Ubuntu

Get the latest .deb package for your distribution from the
[Releases page](https://github.com/fboender/jerrybuild/releases)

Install the package:

    sudo dpkg -i jerrybuild-*.deb

That's it, you're done. You can find the Jerrybuild configuration in
`/etc/jerrybuild`. You can create new jobs in `/etc/jerrybuild/jobs.d`. The
workspace for building your projects can be found in
`/var/lib/jerrybuild/workspace`.

# Redhat / CentOS

Get the latest .deb package for your distribution from the
[Releases page](https://github.com/fboender/jerrybuild/releases)

Install the package:

    sudo dpkg -i jerrybuild-*.deb

That's it, you're done. You can find the Jerrybuild configuration in
`/etc/jerrybuild`. You can create new jobs in `/etc/jerrybuild/jobs.d`. The
workspace for building your projects can be found in
`/var/lib/jerrybuild/workspace`.

# Other

Other Operating Systems can install Jerrybuild using the Makefile in the
repository:

    git clone git@github.com:fboender/jerrybuild.git
    cd jerrybuild/src
    sudo make install

You can find the Jerrybuild configuration in `/etc/jerrybuild`. You can create
new jobs in `/etc/jerrybuild/jobs.d`. The workspace for building your projects
can be found in `/var/lib/jerrybuild/workspace`.
