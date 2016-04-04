#!/usr/bin/python

import json


def normalize(request, project_name, config):
    env = {}
    body = json.load(request.body)
    config_section = 'project:{}'.format(project_name)

    # FIXME: Gogs doesn't implement body signing using hmac yet. See bug
    # https://github.com/gogits/gogs/issues/2256. So we just compare the secret
    # for now, which is insecure.
    if body['secret'] != config.get(config_section, 'secret'):
        raise ValueError("Invalid secret")

    env['event'] = request.headers['X-Gogs-Event']
    env['repo_type'] = 'git'
    env['repo_url'] = body['repository']['clone_url']
    env['repo_url_ssh'] = body['repository']['ssh_url']
    env['repo_url_http'] = body['repository']['clone_url']
    env['ref'] = body['ref']
    env['commit'] = body['after']

    return env
