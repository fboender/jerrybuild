import json


def normalize(request, jobdef):
    env = {}
    body = json.load(request.body)
    secret = jobdef.custom_params['secret']

    if request.headers['X-Gogs-Event'] != 'push':
        raise NotImplementedError("Only push events are currently supported")

    # Gogs doesn't implement body signing using hmac yet. See bug
    # https://github.com/gogits/gogs/issues/2256. So we just compare the secret
    # for now, which is insecure.
    if body['secret'] != secret:
        raise ValueError("Invalid secret")

    env['provider'] = 'gogs'
    env['event'] = request.headers['X-Gogs-Event']
    env['repo_type'] = 'git'
    env['repo_url'] = body['repository']['clone_url']
    env['repo_url_ssh'] = body['repository']['ssh_url']
    env['repo_url_http'] = body['repository']['clone_url']
    env['ref'] = body['ref']
    env['commit'] = body['after']

    mail_to = []
    mail_to.append(body['repository']['owner']['email'])
    mail_to.append(body['pusher']['email'])
    env['mail_to'] = ', '.join(mail_to)

    return env
