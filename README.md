jerrybuild
==========

![Status: Unstable](https://img.shields.io/badge/status-unstable-red.svg)

A lightweight build / CI (Continues Integration) server.

## About

Jerrybuild is a lightweight project build and Continues Integration server
written in Python. It includes a web server with generic webhook support and
plugins for Github and Gogs.

Features:

* Easy to set up.
* Consumes only 16 Mb of memory.
* Written in Python (v2.7+, v3+) with zero other dependencies.
* Webhook plugins for Github, Gogs and generic web hooks.
* Utilizes scripts to do the building.
* Job build queue.
* Send email on job build failures.

Since Jerrybuild is supposed to be lightweight, it doesn't implement some
features found in other CI servers:

* Jerrybuild does not understand your version control system. Updating clones
  and checking out the correct branches should be handled in your build
  script. The Github, Gogs and other providers will pass environment values to
  your script containing information on which repo/commit to build. #FIXME:
  Examples.
* The job build queue can currently only build one job at a time. If this is a
  problem for you, please submit a Github issue requesting this functionality.
* There is no scheduling mechanism. You can use Cron to do scheduled builds.

## Installation

FIXME

## Usage

### Invocation

To run Jerrybuild:

    $ jerrybuild <config.cfg>

### Configuration file

The first step is to create a configuration file for Jerrybuild. This
configuration file will contain some global settings, as well as your build
job specifications.

An example configuration containing comments can be found at FIXME: URL

Here's an shortened example configuration, saved in the file `jerrybuild.cfg`:

    [server]
    listen = 0.0.0.0
    port = 5281
    log_level = INFO
    state_dir = /var/lib/jerrybuild/
    mail_to = dev@example.com

    #
    # Example project: ansible-cmdb
    #
    [project:ansible-cmdb]
    url = /project/ansible-cmdb
    provider = github
    secret = SECRET_TOKEN_HERE
    run = /home/build/ansible-cmdb/run_tests.sh

This configuration file specifies a single build job called `ansible-cmdb`. It
has several configuration options:

* **`url`**: The URL on which Jerrybuild's web server should listen for
  incoming webhook notifications. This option is required.
* **`provider`**: The type of service that will be initiating the webhook
  notification. Values values are: `github`, `gogs` and `generic`. Providers
  help with the parsing of the webhook request into environment variables that
  can be used by your build scripts. This option is required.
* **`secret`**: A setting specific to the Github and Gogs providers. The
  value must match the value specified in the webhook configuration on Github
  or Gogs, so that Jerrybuild can verify that Github or Gogs really made the
  notification.
* **`run`**: The script to run when the webhook is called. Depending on which
  provider you're using, several environment variables will be set with
  information regarding the webhook notification. For example, the Github
  provider will set the `commit` variable to the hash of the last commit on a
  `push` event. This optio is required.

You can specify as many build jobs as you like. They should always start with
`project:`.

We're now ready to run Jerrybuild. To start Jerrybuild, you must pass the
configuration file to be used as the first parameter:

    $ jerrybuild ./jerrybuild.cfg
    2016-04-05 08:11:23,284:INFO:Build queue running
    2016-04-05 08:11:23,284:INFO:Project 'ansible-test' listening on '/project/ansible-test'
    2016-04-05 08:11:23,285:INFO:Server listening on 0.0.0.0:5281

If you configure a new webhook in Github with
`http://yourhost.example.com/project/ansible-cmdb` as the callback URL and
`SECRET_TOKEN_HERE` as the secret token, Github will call Jerrybuild on each
commit (or other action) and the `run_tests.sh` script will be called.

## Reloading

You can reload the configuration file by sending the HUP signal to Jerrybuild:

    $ pidof -x "jerrybuild"
    4718
    $ kill -HUP 4718
    # In log file: 2016-04-15 16:03:31,645:INFO:Reloading configuration file

FIXME: Implement `reload` in init job.

# Providers

Providers are like plugins that understand how to parse webhook callbacks from
different sources such as Github or Gogs. The currently available providers
are:

* Generic. Handles any kind of webhok.
* Github (https://www.github.com)
* Gogs (https://www.gogs.io FIXME)

Providers inspect the webhook HTTP request and extract useful information from
them. This information is passed on to your build script through the
environment. The providers may also perform authentication and authorization.

## Github

## Gogs

Gogs is a lightweight Github clone written in Go.

Unlike Github, Gogs does not use HMAC signing with the secret key on the body.
It simply passes the secret in the body of the request. The Gogs provider
verifies this secret, but you really should run Jerrybuild behind a HTTPS
connection.

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
