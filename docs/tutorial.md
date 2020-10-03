In this tutorial we'll create a Jerrybuild configuration and configure a
simple build job.

In a production environment, you'd install Jerrybuild system-wide instead, but
for this tutorial we'll be working from the git repo.

# Preparation

Create a clone of the repo:

    $ git clone https://github.com/fboender/jerrybuild.git
    $ cd jerrybuild

Now we'll create a directory structure to hold our tutorial example:

    $ mkdir tutorial
    $ mkdir tutorial/jobs.d
    $ mkdir tutorial/status
    $ mkdir tutorial/work_dir

A little explanation is in order. The `jobs.d` directory will hold
configuration files for our various build jobs. The `status` dir is where
Jerrybuild will keep some metadata of each job's status. The `work_dir` is
where Jerrybuild will be doing the actual building.

# Main configuration file

All of these can be configured in the main configuration file. So let's create
that:

    $ vi tutorial/jerrybuild.cfg

And put the following content in it:

    [server]
    listen = 127.0.0.1
    port = 5281
    log_level = INFO
    status_dir = tutorial/status/
    work_dir = tutorial/work_dir/
    keep_jobs = 40

    %include jobs.d/*.cfg
      
This configuration file has no comments, but you can check the [Example
jerrybuild.cfg](https://raw.githubusercontent.com/fboender/jerrybuild/master/example/jerrybuild.cfg)
for an annotated example.

# Job definition configuration

Now it's time to define our first job. Jerrybuild has built-in support for
various "providers", such as Github and Gogs. For now we'll use the "generic"
provider, which doesn't integrate with any specific git hosting site, but can
be called by any webhook callback.

Create a job configuration file in the `jobs.d` directory:

    $ vi tutorial/jobs.d/tutorial.cfg

Put the following contents in it:

    [job:tutorial]
    desc = The jerrybuild tutorial
    url = /hook/tutorial
    provider = generic
    cmd = sh tutorial.sh

Again, we've left out the comments. See the [Example job
configuration](https://raw.githubusercontent.com/fboender/jerrybuild/master/example/jobs.d/example.cfg)
for an annotated example.

The `url` settings specifies by which URL this job can be called. It is
relative to the web root. So if we start Jerrybuild on `http://127.0.0.1:5281/`,
the job's hook url becomes `http://127.0.0.1:5281/hook/tutorial`.

What should happen when the hook is called is defined by the `cmd` setting. In
this case, we tell Jerrybuild that it should call a script called
`tutorial.sh`. This is relative to the main configuration's `work_dir`.

# Create build script

Let's create that shell script!

    $ vi tutorial/work_dir/tutorial.sh

The file should look like this:

    #!/bin/sh

    echo "Hello!"

# Run Jerrybuild and start a build

Time to start Jerrybuild for the first time:

    $ python3 ./jerrybuild.py tutorial/jerrybuild.cfg

The webserver should now be running on
[http://127.0.0.1:5281](http://127.0.0.1:5281). Try opening it in the browser.
You should see a single job called "tutorial" with a grey "Never built" status.So
let's try to build it. We'll use *curl* to call the webhook:

    $ curl http://127.0.0.1:5281/hook/tutorial

If you refresh the webpage, you should now see that the job's status has
changed to a green "Passed" button. You can click on that button to go to that
job's output page. There you can see some job metadata, such as when it was
built, its exit code and the output of the job. It should say "Hello!".

# Clone / pull a repo

Let's do something a little more useful though. We'll have the script clone an
actual git repository or, if it's already been cloned, do a pull & rebase.

Replace the contents of `tutorial/work_dir/tutorial.sh` with:

    #!/bin/sh
    set -x

    REPO="https://github.com/fboender/jerrybuild.git"

    if [ ! -d "jerrybuild" ]; then
        git clone "$REPO"
    else
        cd jerrybuild
        git pull --rebase
        cd ..
    fi

    cd jerrybuild
    ls -la
  
That's right, we're going to clone jerrybuild itself for this tutorial. Hope
that's not confusing!

Note that this will work because Jerrybuild is a public repo. If you need to
clone private repos, have a look at the
[Cookbook: Clone a repo with a custom private
key](../cookbook/#clone-a-repo-with-a-custom-private-key) section.

Go back Jerrybuild's web interface and find the status output of the previous
job we ran. You'll see a blue "Rerun as new job" button. Clicking that is
basically the same as running that `curl` command we saw earlier.

Go ahead and click that, and you should see the repo being cloned and then a
listing of its files. If you click that same button again, you should see that
it's doing a `git pull --rebase` rather than a new clone.

# Github provider

You'll probably want to trigger builds from an external source repository such
as Github. Jerrybuild has [providers](../providers) for that. The providers
have some extra logic to handle webhook callbacks from specific external
repositories. For example, Github lets you configure a secret for your webhook
that ensures the request truly came from Github. Jerrybuild's `github`
provider automatically verifies that secret.

This part of the tutorial assumes you've got Jerrybuild running on a public
server. We'll be using "https://build.electricmonk.nl" as an example. You can
check the [Cookbook](../Cookbook) on how to serve Jerrybuild behind a public
webserver.

We'll also assume you've generated and configured a deploy ssh key. Again, 
check the [Cookbook](../Cookbook) for instructions on how to do that.

We configure a job with the `github` provider.

    $ vi tutorial/jobs.d/github-example.cfg

It should look like this:

    [job:github-example]
    url = /hook/github-example
    provider = github
    secret = eiHeik3xeoGh6ieg8oZingah
    cmd = sh ./github-example.sh

The `secret` is just a randomly generated password.

Next we create the `github-example.sh`.

    $ vi tutorial/work_dir/github-example.sh

Add the following contents to that script:

    #!/bin/sh

    set -x

    export PROJECT="jerrybuild"
    export REPO="https://github.com/fboender/$PROJECT.git"
    export SSH_KEY="/var/lib/jerrybuild/deploy_keys/build_rsa"
    export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o IdentitiesOnly=yes"

    if [ ! -d "$PROJECT" ]; then
        git clone "$REPO"
    else
        cd $PROJECT
        git reset --hard
        git clean -f -d
        git fetch
        cd ..
    fi

    cd $PROJECT
    git checkout -q $commit
    ls -la

Some explanation may be in order...

The script first exports some variables. To reduce repetition, we define the
`PROJECT`. We then point the `SSH_KEY` variable to the private deploy key that
has access to our project in Github. To instruct Git to use that private key,
we set the `GIT_SSH_COMMAND` variable.

Next we either clone the repo if it wasn't cloned yet. Otherwise, we
completely reset the repo to a clean state, and then fetch any new remote
changes from Github.

Finally, we change the current dir to the repo, and check out `$commit`. This
is a special variable set by the `github` provider. It contains the SHA1
commit that triggered this webhook callback in Github.

For demonstration purposes we just list the contents of the repository. This
is normally where you perform your automated tests and other build
instructions.

We now need to restart Jerrybuild or send it the `SIGHUP` signal. Either of
those cause Jerrybuild to reload the configuration so that it spots the new
job.

    $ ps auxf | grep jerrybuild
    jerrybu+  3483  0.0  1.8 507164 37300 ?        Sl   Jun08  40:46 /usr/bin/python /usr/bin/jerrybuild [...]

    $ kill -HUP 3483

Jerrybuild's log file should show:

    2020-10-03 09:24:22,015:INFO:Reloading configuration file

Now it's time to configure the webhook in Github. Go to the projects Settings
and then click on "Webhooks". Add a new webhook with the button at the top
right. 

Enter the payload URL, which should be something like
`https://build.electricmonk.nl/hook/github-example`. Change the Content-type
to `application/json`. Copy-paste the secret from the job's configuration file
into the `Secret` box. For "Which events would you like to trigger this
webhook", we'll keep the default "Just the push event" selection.

Save the webhook by clicking the "Add webhook" button. Github should now send
a "ping" event to test the webhook. Jerrybuild understands those ping events,
so everything should be fine.

Now when you push a new commit to the repository, it should automatically call
the Jerrybuild build job!
