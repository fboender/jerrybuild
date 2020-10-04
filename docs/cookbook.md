The Cookbook contains examples on how to achieve certain common scenarios.

# Managing jerrybuild

This assumes you've installed Jerrybuild system-wide.

Starting jerrybuild:

    sudo systemctl start jerrybuild

Stopping jerrybuild:

    sudo systemctl stop jerrybuild

When you create new job configurations, you'll need to reload Jerrybuild to
make it aware of the new job:

    sudo systemctl reload jerrybuild

View the log output:

    sudo journalctl -u jerrybuild

# Clone a repo with a custom private key

If you want to clone a repo with a custom private key, such as when calling it
in a build script in Jerrybuild.

First create a key:

    ssh-keygen -t ed25519 -N "" -C "deploykey@proj.acc" -f deploy_key_ed25519

This generates a passwordless elliptic curve private key and public key
(`deploy_key_ed25519` and `deploy_key_ed25519`) with comment
"deploykey@proj.acc".

Next, add the public part of the key to your remote repo as a Deployment Key.
Most git repo providers (such as Github, Gogs and Gitlab) support deployment
keys.

Now you can clone and fetch (but not push!) where ever that private key
exists:

    $ export GIT_SSH_COMMAND='ssh -i /path/to/key/id_ed25519 -o IdentitiesOnly=yes'
    $ git clone git@github.com:fboender/myprivaterepo.git

See the [Example build
script](https://github.com/fboender/jerrybuild/blob/master/example/work_dir/example.sh)
for a full example on how to clone your repos.


# Scheduled builds

You can schedule builds (e.g. nightly builds) using a cron job. For this we'll
use `wget` and the `generic` provider. Say we have the following job
definition:

    [job:foomatic-nightly]
    desc = Make nightly release builds of Foomatic
    url = /hook/foomatic-nightly
    provider = generic
    cmd = foomatic-nightly.sh

We can automatically build this each night at 01:00 with a cron job:

    # m  h  dom mon dow command
    0    1  *   *   *   wget -q -O - http://example.com/hook/foomatic-nightly > /dev/null

When you're using a different provider, such as `github`, you won't be able to
call that same hook using `wget` or `curl`. This is because those providers
send authentication tokens which are validated by Jerrybuild when an incoming
hook triggers.

Instead you'll have to set up a separate build job with the `generic`
provider.


# Link to a job's Shield

Jerrybuild has support for [Shields](https://www.shields.io/). You can create
an image that is a link to your project's shield. The following example
assumes Jerrybuild is running at `example.org` behind an Nginx web server.
Nginx should be configured to pass requests for shields to the Jerrybuild
backend serrver:

    # Pass requests for shields through to Jerrybuild for anyone. Caching
    # is turned off.
    location ~ /job/.*/shield {
        proxy_pass http://127.0.0.1:5281;
        expires off;
    }

Now you create an image anywhere that points the job's shield:

    <img src="https://example.org/job/foomatic-nightly/shield" alt="build
    status" />


# Serving Jerrybuild behind a webserver

Jerrybuild's built-in webserver should not be publicly exposed on the
Internet. Rather, you should serve requests from Apache or Nginx and configure
them to proxy requests between the Jerrybuild webserver.

## Apache

TODO: Document this.

## Nginx

Since Jerrybuild contains some sensitive user operations such as rerunning
jobs, we want to protect the sensitive stuff with some authentication
mechanism, but leave the public parts (the webhooks and shields) open.

The following Nginx configuration does just that:

    server {
        listen 80;

        server_name build.electricmonk.nl;
        root /var/www/build.electricmonk.nl/htdocs;

        access_log /var/www/build.electricmonk.nl/logs/access.log;
        error_log /var/www/build.electricmonk.nl/logs/error.log;

        location / {
            return 302 https://$host$request_uri;
        }
        location /.well-known/ {
            default_type "text/plain";
        }
    }
    server {
        listen 443 ssl;

        server_name build.electricmonk.nl;

        ssl_certificate /etc/acme/build.electricmonk.nl/fullchain.cer;
        ssl_certificate_key /etc/acme/build.electricmonk.nl/build.electricmonk.nl.key;

        access_log /var/www/build.electricmonk.nl/logs/access.log;
        error_log /var/www/build.electricmonk.nl/logs/error.log;

        root /var/www/build.electricmonk.nl/htdocs/;
        index index.html index.htm;

        # Allow letsencrypt web doc root requests without requiring
        # authentication.
        location /.well-known {
        }

        # Proxy pass requests for shields to Jerrybuild without requiring
        # authentication.
        location ~ /job/.*/shield {
            proxy_pass http://127.0.0.1:5281;
            expires off;
        }

        # Proxy pass requests for hooks to Jerrybuild without requiring
        # authentication.
        location /hook {
            proxy_pass http://127.0.0.1:5281;
        }

        # All other requests require authentication.
        location / {
            auth_basic "Restricted";
            auth_basic_user_file /var/www/build.electricmonk.nl/data/htpasswd;
            proxy_pass http://127.0.0.1:5281;
        }
    }

You can generate the `htpasswd` file using Apache utils (yes, even for Nginx):

    $ sudo apt-get install apache2-utils
    $ sudo htpasswd -c /var/www/build.electricmonk.nl/data/htpasswd yourusername
