jerrybuild
==========

![Status: Unstable](https://img.shields.io/badge/status-unstable-red.svg)
![Build Status](http://git.electricmonk.nl/job/jerrybuild/shield)
![Activity: Active development](https://img.shields.io/badge/activity-active%20development-green.svg)
![License: GPLv3](https://img.shields.io/badge/license-GPLv3-blue.svg)


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
* Send email on job build failures and recovery.
* Web interface front-end.
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

### Run from repo

If you just want to evaluate Jerrybuild, it's possible to run Jerrybuild
directly from the git reposiroty. When you're satisfied that you really wish
to use Jerrybuild, you can install it on your system.

### Install system-wide

Get the package for your distribution from the [Releases
page](https://github.com/fboender/jerrybuild/releases).

For Debian / Ubuntu systems:

    sudo dpkg -i jerrybuild-*.deb

To install from source / the Git repo:

    git clone https://github.com/fboender/jerrybuild.git
    cd jerrybuild
    sudo make install

The packages and `make install` install Jerrybuild system-wide and:

* Creates a `jerrybuild` user which will own the configuration files and
  working space.
* Put the global configuration in `/etc/jerrybuild/jerrybuild.cfg`.
* Put the job configuration in `/etc/jerrybuild/jobs.d`.
* Creates the working space for your repositories in
  `/var/lib/jerrybuild/workspace`/.

## Getting started

There's also a more in-depth full [Tutorial]() available.

For this example, we'll be building a project named `my-project`. It uses Git
and is hosted on Github.

Create a new job: `/etc/jerrybuild/jobs.d/my-project`:

    [job:my-project]
    desc = Build MyProject
    url = /hook/my-project
    provider = generic
    cmd = /var/lib/jerrybuild/workspace/my-project/build.sh

This defines a new job that will listen on the URL
`http://localhost:5281/hook/my-project`, depending on the settings in the
global configuration file. The provider is `generic`, which supports basically
any SCM that can do POST requests. When a POST is made to the hook URL,
Jerrybuild will execute the
`/var/lib/jerrybuild/workspace/my-project/build.sh` script. Before doing so,
it will change to the `work_dir` configured in the global configuration file.

Next, git clone your project into the correct directory:

    $ cd /var/lib/jerrybuild/workspace/
    $ git clone git@github.com:yourusername/my-project.git

You may need to do this as the `jerrybuild` user, or otherwise probably want
to change the ownership of the project to the `jerrybuild` user afterwards:

    $ sudo chown -R jerrybuild:jerrybuild my-project

You're completely free to implement `build.sh` as you see fit. It might look
something like this though:

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

Add public key to know hosts:

    ssh github.com
    The authenticity of host 'github.com (192.30.253.113)' can't be established.
    RSA key fingerprint is 16:27:ac:a5:76:28:2d:36:63:1b:56:4d:eb:df:a6:48.
    Are you sure you want to continue connecting (yes/no)? yes
    Warning: Permanently added 'github.com,192.30.253.113' (RSA) to the list
    of known hosts.

Start Jerrybuild:

    $ jerrybuild /etc/jerrybuild/jerrybuild.cfg

Configure the webhook in Github. FIXME

## Tools

Jerrybuild itself doesn't know how to check out your source code, but it does
provide tools to make it easier to do so. The tools come in the form of
shellscripts. You can find them in the [src/tools](src/tools) directory.

The directory containing the tools is automatically included in the PATH when
your build script is being run, so you can use it right from your buildscript.
