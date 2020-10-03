Providers are like plugins that understand how to parse webhook callbacks from
different sources such as Github or Gogs. The currently available providers
are:

* `generic`: A generic handler that handles any kind of webhok.
* `github`: [Github](https://www.github.com)
* `gogs`: [Gogs](https://gogs.io/)

Providers inspect the webhook HTTP request and extract useful information from
it. This information is passed on to your build script through the
environment. The providers may also perform authentication and authorization.

## Generic

The `generic` provider is the default provider. It is independent of the
remote Git repository used (e.g. Github). You can use it to trigger builds
from cronjobs and unsupported build systems.

The following environment variables are currently passed to scripts when using
the Github provider:

    provider=generic

Additionally, the request HTTP headers are added to the environment, as well
as any configuration `env_` settings from the main configuration or job
definition. Example:

    HEADER_CONTENT-TYPE=application/x-www-form-urlencoded
    HEADER_ACCEPT=*/*
    HEADER_CONNECTION=Keep-Alive
    HEADER_CONTENT-LENGTH=14
    HEADER_HOST=localhost:5281
    HEADER_USER-AGENT=Wget/1.15 (linux-gnu)
    GIT_SSH=git-wrapper.sh
    SSH_KEY=/var/lib/jerrybuild/foo/test.rsa

Since the generic provider cannot make any assumptions about the request, the
environment depends on what the client has sent.

## Github

Github is a git repository provider. The Github provider in Jerrybuild offers
support for handling webhook callbacks from Github. Currently, the following
events are supported:

* ping
* push

The Github provider requires the following additional settings in job
configurations:

* **`secret`**: A secret to be used for HMAC body verification. The secret
should also be configured in the Webhook configuration on Github. Github will
sign the body using HMAC hashing using the key. Jerrybuild can then verify the
signature.

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

Additionally, the request HTTP headers are added to the environment, as well
as any configuration `env_` settings from the main configuration or job
definition. Example:

FIXME: Include example of Github request headers.

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

Additionally, the request HTTP headers are added to the environment, as well
as any configuration `env_` settings from the main configuration or job
definition. Example:

FIXME: Include example of Gogs request headers.


