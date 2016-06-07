jerrybuild
==========

![Status: Unstable](https://img.shields.io/badge/status-unstable-red.svg)

A lightweight build / CI (Continuous Integration) server.

## About

Jerrybuild is a lightweight project build and Continuous Integration server
written in Python. Basically, it's a web server that listens for webhook
notifications and then runs scripts.

Features:

* Easy to set up and configure via a simple configuration file
* Consumes only 17 Mb of memory
* Support for generic webhooks, Github and Gogs
* Written in Python (v2.7+, v3+) with zero other dependencies
* Utilizes scripts to do the building. Any programming language can be used to
  create build scripts.
* Pass custom environment variables to the scripts based on globally
  or job-specificly configured environment settings.
* Send email on job build failures
* Web interface front-end
* Shield support (http://shields.io/)

Since Jerrybuild is supposed to be lightweight, it doesn't implement some
features found in other CI servers:

* Jerrybuild does not control your version control system for you. Updating
  clones and checking out the correct branches should be handled in your build
  script. The Github, Gogs and other providers will pass environment values to
  your script containing information on which repo/commit to build. #FIXME:
  Examples.
* The job build queue can currently only build one job at a time. 
* Jerrybuild cannot be configured via the web interface, only via the
  configuration file.
* Jerrybuild doesn't try to do things other programs are better at. As such:
  - There is no scheduling mechanism. You can use Cron to do scheduled builds.
  - The web interface has no authentication. If you require authentication,
    you should put Apache or Nginx in front of it. See the Cookbook for a
    How-to.
  - Doesn't support SSL. Put Apache or Nginx in front of it. See the Cookbook
    for a How-to.


## Installation

Get the package for your distribution from the
[Releases page](https://github.com/fboender/jerrybuild/releases) (Not required
for MacOS X install)

For Debian / Ubuntu systems:

    sudo dpkg -i jerrybuild-*.deb

To install from the Git repo:

    git clone https://github.com/fboender/jerrybuild.git
    cd jerrybuild
    make install

## Getting started

This section assumes you've installed the Ubuntu package. If not, please
modify the paths accordingly. Note that it's possible to run Jerrybuild
directly from the Git repository.

There's also a more in-depth full [Tutorial]() available.

For this example, we'll be building a project named `my-project`. It uses Git
and is hosted on Github.

First, **review the configuration** in `/etc/jerrybuild/jerrybuild.cfg'.

Next, create a new job: `/etc/jerrybuild/jobs.d/my-project`:

    [job:my-project]
    desc = Build MyProject
    url = /hook/my-project
    provider = github
    secret = thooRohmooroot3ha1ohf7menozei9ni
    cmd = /var/lib/jerrybuild/workspace/my-project/build.sh

Git clone your project:

    $ cd /var/lib/jerrybuild/workspace/
    $ git clone git@github.com:yourusername/my-project.git

The `build.sh` in your project would look something like this, assuming we
want to build `master` branch:

    $ cd my-project
    $ cat build.sh
    #!/bin/sh

    set -e

    export SSH_KEY="/var/lib/jerrybuild/deploy_keys/my-project.rsa"
    export GIT_SSH=git_wrapper.sh

    cd my-project

    git checkout master
    git reset --hard
    git clean -f -d
    git pull --rebase
    git checkout $commit

    make test
    make release REL_VERSION=9.99

Start Jerrybuild:

    $ jerrybuild /etc/jerrybuild/jerrybuild.cfg

Configure the webhook in Github. FIXME


