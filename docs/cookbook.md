The Cookbook contains exxamples on how to achieve certain common scenarios.

## Serving Jerrybuild over HTTP(s)

Jerrybuild's built-in webserver should not be publicly exposed on the
Internet. Rather, you should serve requests from Apache or Nginx and configure
them to proxy requests between the Jerrybuild webserver.

### Run behind Apache

TODO: Document this.

### Run behind Nginx

I'll assume you've already gotten SSL certificates and placed them in
`/etc/nginx/certs/`.

We set up a non-SSL virtualhost to forward all requests to the SSL site:

    server {
        listen 80;

        server_name git.electricmonk.nl;
        root /var/www/git.electricmonk.nl/htdocs;

        access_log /var/www/git.electricmonk.nl/logs/access.log;
        error_log /var/www/git.electricmonk.nl/logs/error.log;

        location / {
            return 301 https://$host$request_uri;
        }
    }

Then we set up a SSL virtualhost that proxies requests to a running Jerrybuild
instance. You don't need to open the Jerrybuild port to the outside world for
this, and you can let specific requests through depending on IP:

    server {
        listen 443 ssl;

        server_name git.electricmonk.nl;

        ssl_certificate /etc/nginx/certs/git.electricmonk.nl/fullchain.cer;
        ssl_certificate_key /etc/nginx/certs/git.electricmonk.nl/git.electricmonk.nl.key;

        access_log /var/www/git.electricmonk.nl/logs/access.log;
        error_log /var/www/git.electricmonk.nl/logs/error.log;

        root /var/www/git.electricmonk.nl/htdocs;
        index index.html index.htm index.php;

        # Pass requests for shields through to Jerrybuild for anyone. Caching
        # is turned off.
        location ~ /job/.*/shield {
            proxy_pass http://127.0.0.1:5281;
            expires off;
        }

        # Pass webcall hook notifications through to Jerrybuild from any IP.
        location /hook {
            proxy_pass http://127.0.0.1:5281;
        }
    }

### Authentication with Apache

### Authentication with Nginx

## Webhooks

The meat of Jerrybuild is, of course, its support for webhooks. 

### Build when a new commit is pushed

The `git-co-commit.sh` tool provided with Jerrybuild is ideal for checking out
any commits that are pushed to repositories. The following example will clean
a local repository clone, fetch all new changes and check out the commit given
in the `commit` environment variable. This variable is generally set by the
Providers (Github, etc):

    #!/bin/sh
    
    set -e
    
    export SSH_KEY="/var/lib/jerrybuild/deploy_keys/my-project.rsa"
    export GIT_SSH=git_wrapper.sh  # Provided by Jerrybuild
    
    cd my-project
    git-co-commit.sh  # Provided by Jerrybuild
    make test
    make release REL_VERSION=9.99

### Build when a new tag is pushed

TODO: Document this.

### Build only a specific branch

TODO: Document this.

### Build a merge request

TODO: Document this.

## Other

### Run a build on a remote machine]

TODO: Document this.

### Scheduled builds

TODO: Document this.

### Link to a job's Shield

TODO: Document this.
