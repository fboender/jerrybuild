#!/usr/bin/python

import hmac
import hashlib
import json


def normalize(request, project_name, config):
    env = {}
    raw_body = request.body.read()
    body = json.load(request.body)
    config_section = 'project:{}'.format(project_name)
    secret = bytes(config.get(config_section, 'secret').strip())

    if request.headers['X-Github-Event'] != 'push':
        raise NotImplementedError("Only push events are currently supported")

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

