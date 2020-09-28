import hmac
import hashlib
import json
from ..bottle import response


def normalize(request, jobdef):
    if request.headers['X-Github-Event'] == 'ping':
        response.status = 200
        response.body = "pong"
        return False

    env = {}
    raw_body = request.body.read()
    body = json.load(request.body)
    secret = bytes(jobdef.custom_params['secret'])

    if request.headers['X-Github-Event'] != 'push':
        raise NotImplementedError("Only push and ping events are currently supported")

    # Verify hash signature
    hashtype, signature = request.headers['X-Hub-Signature'].split('=', 1)
    if hashtype != 'sha1':
        raise ValueError("Invalid hashtype received")

    res = hmac.new(secret, msg=raw_body, digestmod=hashlib.sha1)
    # Python <2.7 doesn't have a secure compare for hmac, so we just compare
    # manually. This leaves this code vulnerable to timing attacks,
    # unfortunately.
    if str(res.hexdigest()) != str(signature):
        raise ValueError("Invalid secret")

    env['provider'] = 'github'
    env["event"] = request.headers['X-Github-Event']
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

