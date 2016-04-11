#!/usr/bin/python

import hmac
import hashlib


def normalize(request, project_name, config):
    env = {}
    body = request.body.read()
    config_section = 'project:{}'.format(project_name)
    secret = config.get(project_name, 'secret')

    if request.headers['X-Github-Event'] != 'push':
        raise NotImplementedError("Only push events are currently supported")

    # Verify hash signature
    hashtype, signature = self.headers['X-Hub-Signature'].split('=', 1)
    if hashtype != 'sha1':
        raise ValueError("Invalid hashtype received")

    mac = hmac.new(secret, msg=data, digestmod=hashlib.sha1)
    match = hmac.compare_digest(mac.hexdigest(), signature)
    if not match:
        raise ValueError("Invalid secret")

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

