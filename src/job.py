#!/usr/bin/python

import os
import logging
import Queue
import uuid
import subprocess


class Job:
    def __init__(self, project, env, cmd, work_dir=None, id=None, mail_to=[]):
        self.project = project
        self.env = env
        self.set_cmd(cmd, work_dir)
        if id is not None:
            self.id = id
        else:
            self.id = uuid.uuid4().hex
        self.mail_to = mail_to
        self.status = None
        self.exit_code = None
        self.stdout = None
        self.stderr = None

    def set_cmd(self, cmd, work_dir=None):
        if work_dir is not None:
            work_dir = os.path.realpath(work_dir)
            if cmd.startswith('/'):
                cmd = os.path.realpath(cmd)
            else:
                cmd = os.path.realpath(os.path.join(work_dir, cmd))
        else:
            if cmd.startswith('/'):
                work_dir = os.path.realpath(os.path.dirname(cmd))
                cmd = os.path.realpath(cmd)
            else:
                work_dir = os.path.realpath(os.curdir)
                cmd = os.path.realpath(os.path.join(work_dir, cmd))

        self.work_dir = work_dir
        self.cmd = cmd

    def set_status(self, status):
        self.status = status

    def run(self):
        p = subprocess.Popen(self.cmd,
                             cwd=self.work_dir,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=self.env)
        self.stdout, self.stderr = p.communicate(input)
        self.exit_code = p.returncode

    def to_dict(self):
        d = {
            'project': self.project,
            'env': self.env,
            'cmd': self.cmd,
            'work_dir': self.work_dir,
            'id': self.id,
            'status': self.status,
            'exit_code': self.exit_code,
            'stdout': self.stdout,
            'stderr': self.stderr,
        }
        return d

    def __repr__(self):
        return "job '{}', project={}".format(self.id, self.project)
