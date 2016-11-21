## Main configuration file

The main configuration file is location in `/etc/jerrybuild/jerrybuild.cfg`.
Here's an unannotated example configuration:

    [server]
    listen = 127.0.0.1
    port = 5281
    server_url = http://build.example.com
    log_level = INFO
    mail_to = dev@example.com, manager@example.com

    status_dir = /var/lib/jerrybuild/
    work_dir = /var/lib/jerrybuild/workspace
    keep_jobs = 40

    env_SSH_DEPLOY_KEY_DIR = /var/lib/jerrybuild/deploy_keys/

    %include /etc/jerrybuild/jobs.d/*.cfg

Available configuration options:

* **`listen`**: Address to listen on. Instead of changing this to listen on
  external IPs, you'd be better off putting Jerrybuild behind Apache or NGinx.
  See the Cookbook on how to easily do that.
* **`port`**: Port to listen on
* **`log_level`**: The logging level. Logging level. Possible values: DEBUG,
  INFO, WARN, ERROR, FATAL
* **`mail_to`**: Always send mail to recipients on build failure (optional).
  Multiple addresses should be separated by a comma. You can add additional
  addresses in each job section.
* **`status_dir`**: Directory to keep job status files and such in.
* **`work_dir`**: Default working directory for jobs.
* **`keep_jobs`**: The number of job results or a timespan after which to
  delete old job results. This value applies to each job seperately. The last
  job status will never be deleted. This value can be overridden on a
  job-by-job basis in the job's configuration section. Examples: `keep_jobs =
  0` (Keep an infinite number of jobs), `keep_jobs = 10`  (Keep the last 10
  job results), `keep_jobs = 4d` (Remove job results older than 4 days).
* **`env_XXXXX`**: You can define global environment variables that will be
  set for all scripts. For example, env_SSH_DEPLOY_KEY_DIR would result in an
  environment variable SSH_DEPLOY_KEY_DIR in your scripts.

## Defining jobs

Jobs are defined in either the main configuration file or in separate job
configurations that go in `/etc/jerrybuild/jobs.d`. For example, the following
job shows how to run the tests for the
[Ansible-cmdb](https://github.com/fboender/ansible-cmdb) Github project:

    $ cat /etc/jerrybuild/jobs.d/ansible-cmdb_tests.cfg
    
    [job:ansible-cmdb-tests]
    desc = Run Ansible-cmdb tests
    url = /hook/ansible-cmdb-tests
    provider = github
    secret = thooRohmooroot3ha1ohf7menozei9ni
    cmd = /var/lib/jerrybuild/workspace/ansible-cmdb/ansible-cmdb-tests.sh

This defines a job called `ansible-cmdb-test`. Each job should have its own
`[job:XXXXXXXX]` section.

Configuration options explained:

* **`desc`**: A description of the build job.
* **`url`**: The URL on which Jerrybuild's web server should listen for
  incoming webhook notifications. This option is required and has to be unique
  per job.
* **`provider`**: The type of service that will be initiating the webhook
  notification. Values values are: `github`, `gogs` and `generic`. Providers
  help with the parsing of the webhook request into environment variables that
  can be used by your build scripts. This option is required.
* **`secret`**: A setting specific to the Github and Gogs providers.
  The value must match the value specified in the webhook configuration on
  Github or Gogs, so that Jerrybuild can verify that Github or Gogs really
  made the notification. This option is optional depending on the provider
  used.
* **`cmd`**: The shell command to run when the webhook is called. Depending on
  which provider you're using, several environment variables will be set with
  information regarding the webhook notification. For example, the Github
  provider will set the `commit` variable to the hash of the last commit on a
  `push` event. The command is executed relative to the local or global
  (`[server`]) `work_dir` option. If the script returns with exit code 255,
  the build is aborted. This is useful when you want to run a pre-check to see
  if you even want to build at all. Jerrybuild pretends the build never
  happened. Otherwise, an exit code of 0 indicates success, > 0 indicates
  failure. This option is required.

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
* **`env_XXXX`**: An environment variable to pass to the command.

## Running Jerrybuild

### Manually

We're now ready to run Jerrybuild. To start Jerrybuild, you must pass the
configuration file to be used as the first parameter:

    $ jerrybuild /etc/jerrybuild/jerrybuild.cfg
    2016-04-25 07:36:41,014:INFO:Build queue running
    2016-04-25 07:36:41,015:INFO:Server listening on 0.0.0.0:5281

If you configure a new webhook in Github with
`http://yourhost.example.com/hook/ansible-cmdb` as the callback URL and
`SECRET_TOKEN_HERE` as the secret token, Github will call Jerrybuild on each
commit (or other action) and the `run_tests.sh` script will be called.

### On system boot (init script)

If you installed Jerrybuild through the Debian or Redhat package, an init file
will have been placed in the usual location. # FIXME location

FIXME

### Reloading

After changing the configuration file, you can reload it by sending the HUP
signal to the Jerrybuild process:

    $ pidof -x "jerrybuild"
    4718
    $ kill -HUP 4718
    # In log file: 2016-04-15 16:03:31,645:INFO:Reloading configuration file

## Providers

Providers are like plugins that understand how to parse webhook callbacks from
different sources such as Github or Gogs. The currently available providers
are:

* `generic`: A generic handler that handles any kind of webhok.
* `github`: [Github](https://www.github.com)
* `gogs`: [Gogs](https://gogs.io/)

Providers inspect the webhook HTTP request and extract useful information from
them. This information is passed on to your build script through the
environment. The providers may also perform authentication and authorization.

### Github

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

### Gogs

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

# Tools

To ease the creation of build scripts, Jerrybuild provides some tools
out-of-the-box. These are automatically places in the PATH when the command is
run.

## git-wrapper.sh

**`git-wrapper.sh`** is a wrapper for Git that sets the SSH (deploy) key. When
you point the `GIT_SSH` environment variable to `git-wrapper.sh`, Git will use
it to perform git commands. The `git-wrapper.sh` script reads the path to your
SSH key from the `SSH_KEY` variable.

You can set the `SSH_KEY` variable either in your build scripts, globally in
the Jerrybuild main configuration or in the job definition.

Example usage:

    export SSH_KEY=/path/to/ssh_key.rsa
    export GIT_SSH=git_wrapper.sh
    
    git fetch --all
    git checkout master

## git-co-commit.sh

**`git-co-commit.sh`** resets a git repository to a good clean state, fetches
all new changes and checks out the commit given in the `commit` environment
variable.

The `commit` environment variable is generally automatically set by the
provider, such as Github.

Example usage:

    export SSH_KEY=/path/to/deploy_key.rsa
    export GIT_SSH=git_wrapper.sh
    
    git-co-commit.sh
