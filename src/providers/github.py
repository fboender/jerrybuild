#!/usr/bin/python

import hmac
import hashlib


def normalize(request, project_name, config):
    # Verify hash signature
    body = request.body.read()
    print body
    hash = hmac.new(bytes('4bier4u2'), msg=body, digestmod=hashlib.sha1)

    print hash.hexdigest()
    env = {}
    env["event"] = request.headers['X-Github-Event']
    return env

