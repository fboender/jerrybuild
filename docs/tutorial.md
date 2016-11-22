This section assumes you've installed Jerrybuild system-wide on your system.

* The main configuration file is in `/etc/jerrybild/jerrybuild.cfg`.
* The state directory resides in `/var/lib/jerrybuild` and the workspace is
  found in `/var/lib/jerrybuild/workspace`/.

If you're running directly from the Github repository, you'll have to create
the state and workspace directory, and modify the `contrib/jerrybuild.cfg`
configuration file to match.

For this example, we'll be building a project named `my-project`. It uses Git
and is hosted on Github.

# The main configuration file

The main configuration file can be found in `/etc/jerrybuild/jerrybuild.cfg`.
It can contain both the main `[server]` settings, as well as jobs definitions.
It's more common to put job definitions in separate files in the `jobs.d`
directory though.

Take a look through the included configuration file to see which options are
available. Everything is documented with comments. There is probably little
reason to modify anything except for the `server_url` setting, which
determines how self-referring links are built up.

You can add *environment variables* to this main configuration by adding a
configuration option that starts with `env_`. This environment variable will
become available in all jobs.

For now, we are going to **change** the `listen` setting from:

    listen = 127.0.0.1

to

    listen = 0.0.0.0

This makes Jerrybuild listen on the public interfaces / IPs of your server.
This ensures Github can reach Jerrybuild. Please note that **this is not
recommanded** and we're only doing this for the tutorial's purpose. In real
life, you'll want to run Jerrybuild *behind Apache or Nginx*. See the Cookbook
for info on how to do that.

More information on the main configuration file can be found in the [User
Guide](../user_guide)


# Creating a new job

Jobs can be defined in the main configuration file, or you can add them as
separate files in the `jobs.d` directory in `/etc/jerrybuild`. These files
*must* end with `.cfg`.

Take a look at the `EXAMPLE.cfg` job for the possibilities. This job
configuration will be skipped automatically by Jerrybuild.

Here's an example of a job for the "my-project" project that is hosted on
Github: `/etc/jerrybuild/jobs.d/my-project.cfg`.

    [job:my-project]
    desc = Build MyProject
    url = /hook/my-project
    provider = github
    secret = thooRohmooroot3ha1ohf7menozei9ni
    cmd = /var/lib/jerrybuild/workspace/my-project/build.sh

The `url` determines at which URL the webhook will listen.

The `provider` determines how the webhook acts. Currently, providers for
generic webhooks, Github and Gogs are available. Some providers have different
requirements. For example, the Github provider requires a `secret` key to be
present in your job definition. The secret is also added to the Github
repository. Github then digitally signs the payload of the webhook callback
using HMAC. The `github` provider in Jerrybuild automatically verifies this
signature.

For more documentation and available options, check out the included
`EXAMPLE.cfg` file.

Now, go ahead and create `/etc/jerrybuild/jobs.d/my-project.cfg` with the
contents given above.

# Initializing the workspace

Jerrybuild doesn't clone your project for you, so you'll have to do that
yourself.

Git clone your project:

    $ cd /var/lib/jerrybuild/workspace/
    $ git clone git@github.com:yourusername/my-project.git

# Creating the build script

We'll now create the `build.sh` script that will build the project. 
The `build.sh` in your project would look something like this, assuming we
want to build `master` branch:

    $ cd my-project
    $ cat build.sh
    #!/bin/sh

    set -e

    export SSH_KEY="/var/lib/jerrybuild/deploy_keys/my-project.rsa"
    export GIT_SSH=git_wrapper.sh

    cd my-project

    # The git-co-commit.sh  tool provided with Jerrybuild does the same as the
    # these commands:
    git checkout master
    git reset --hard
    git clean -f -d
    git pull --rebase
    git checkout $commit

    make test
    make release REL_VERSION=9.99

Start Jerrybuild:

    $ jerrybuild /etc/jerrybuild/jerrybuild.cfg

# Configure the webhook

Configure the webhook in Github. FIXME
