The Cookbook contains exxamples on how to achieve certain common scenarios.

## Serving Jerrybuild over HTTP(s)

### Run behind Apache

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

### Build when a new commit is pushed

### Build when a new tag is pushed

### Build only a specific branch

### Build a merge request

## Build scripts

## Other

### Run a build on a remote machine]

### Scheduled builds

### Link to a job's Shield

