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
* Utilizes scripts to do the building
* Pass custom environment variables to the scripts based on globally
  or job-specificly configured environment settings.
* Send email on job build failures
* Web interface front-end

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


## Getting started

### Installation

FIXME


### Create a configuration file

The first step is to create a configuration file for Jerrybuild. This
configuration file will contain some global settings, as well as your build
job specifications.

A full example configuration containing comments can be found at FIXME: URL

Here's an shortened example configuration, saved in the file `jerrybuild.cfg`:

    [server]
    listen = 0.0.0.0
    port = 5281
    state_dir = /var/lib/jerrybuild/
    mail_to = dev@example.com

    #
    # Example job: ansible-cmdb
    #
    [job:ansible-cmdb]
    desc = Run Ansible-cmdb tests
    url = /hook/ansible-cmdb-tests
    provider = github
    secret = SECRET_TOKEN_HERE
    cmd = /home/build/ansible-cmdb/ansible-cmdb-tests.sh

This configuration file specifies a single build job called `ansible-cmdb`. It
has several configuration options:

* **`desc`**: A description of the build job.
* **`url`**: The URL on which Jerrybuild's web server should listen for
  incoming webhook notifications. This option is required and has to be unique
  per job.
* **`provider`**: The type of service that will be initiating the webhook
  notification. Values values are: `github`, `gogs` and `generic`. Providers
  help with the parsing of the webhook request into environment variables that
  can be used by your build scripts. This option is required.
* **`secret`**: A setting specific to the Github and Gogs providers. The
  value must match the value specified in the webhook configuration on Github
  or Gogs, so that Jerrybuild can verify that Github or Gogs really made the
  notification.
* **`cmd`**: The script to run when the webhook is called. Depending on which
  provider you're using, several environment variables will be set with
  information regarding the webhook notification. For example, the Github
  provider will set the `commit` variable to the hash of the last commit on a
  `push` event. This option is required.

You can specify as many build jobs as you like. They should always start with
`job:`.

There are a few other options you can use when defining a job:

* **`work_dir`**: The directory to which to change before running the `cmd`.
  If not given, but one if given in the `[server]` section, that one will be
  used instead. Otherwise, it will default to the directory of the executable
  given in `cmd`.
* **`mail_to`**: Email addresses to send job build failures to. You may
  specify multiple addresses by separating them with a comma. The addresses
  given in this `mail_to` will be combined with those given in the `[server]`
  section.

You can find more information on the configuration file in the full documented
example configuration file. # FIXME Link

### Start Jerrybuild

We're now ready to run Jerrybuild. To start Jerrybuild, you must pass the
configuration file to be used as the first parameter:

    $ jerrybuild ./jerrybuild.cfg
    2016-04-25 07:36:41,014:INFO:Build queue running
    2016-04-25 07:36:41,015:INFO:Server listening on 0.0.0.0:5281

If you configure a new webhook in Github with
`http://yourhost.example.com/hook/ansible-cmdb` as the callback URL and
`SECRET_TOKEN_HERE` as the secret token, Github will call Jerrybuild on each
commit (or other action) and the `run_tests.sh` script will be called.

## Reloading

After changing the configuration file, you can reload it by sending the HUP
signal to the Jerrybuild process:

    $ pidof -x "jerrybuild"
    4718
    $ kill -HUP 4718
    # In log file: 2016-04-15 16:03:31,645:INFO:Reloading configuration file

FIXME: Implement `reload` in init job.

## Automatically start at boot

If you installed Jerrybuild through the Debian or Redhat package, an init file
will have been placed in the usual location. # FIXME location

# Providers

Providers are like plugins that understand how to parse webhook callbacks from
different sources such as Github or Gogs. The currently available providers
are:

* `generic`: A generic handler that handles any kind of webhok.
* `github`: [Github](https://www.github.com)
* `gogs`: [Gogs](https://gogs.io/)

Providers inspect the webhook HTTP request and extract useful information from
them. This information is passed on to your build script through the
environment. The providers may also perform authentication and authorization.

## Github

Github is a git repository provider. The Github provider in Jerrybuild offers
support for handling webhook callbacks from Github. Currently, the following
events are supported:

* ping
* push

The Github provider requires the following additional settings in job
configurations:

* **`secret`**: A secret to be used for HMAC body verification. The secret
should also be configured in the Webhook at Github. Github will sign the body
using HMAC hashing using the key. Jerrybuild can then verify the signature.

The following environment variables are currently passed to scripts when using
the Github provider:

    event = push
    commit = 76dd3f25c8c2ca26854035bd78bbca274aeb40be
    mail_to = user@example.com, user2@example.com
    provider = github
    ref = refs/heads/master
    repo_type = git
    repo_url = https://github.com/fboender/ansible-test.git
    repo_url_http = https://github.com/fboender/ansible-test.git
    repo_url_ssh = git@github.com:fboender/ansible-test.git

## Gogs

Gogs is a lightweight Github clone written in Go.

Unlike Github, Gogs does not use HMAC signing with the secret key on the body.
It simply passes the secret in the body of the request. The Gogs provider
verifies this secret, but you really should run Jerrybuild behind a HTTPS
connection to prevent people from seeing the secret.

The following environment variables are currently passed to scripts when using
the Gogs provider:

    event = push
    repo_type = git
    repo_url_ssh = git@git.electricmonk.nl:fboender/ansible-test.git
    repo_url = http://git.electricmonk.nl/fboender/ansible-test.git
    repo_url_http = http://git.electricmonk.nl/fboender/ansible-test.git
    ref = refs/heads/master
    commit = 1f41a02e9f47b7a9dcc66d1d559c495c7df1fd34
    mail_to = user@example.com, user2@example.com

