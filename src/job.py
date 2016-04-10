#!/usr/bin/python

import os
import logging
import uuid
import subprocess


class Job:
    def __init__(self, jobspec, env, mail_to=[], default_work_dir=None):
        self.jobspec = jobspec
        self.env = env
        self.id = uuid.uuid4().hex
        self.mail_to = mail_to
        self.default_work_dir = default_work_dir
        self.status = None
        self.exit_code = None
        self.stdout = None
        self.stderr = None

    #def set_cmd(self, cmd, work_dir=None):
    #    if work_dir is not None:
    #        work_dir = os.path.realpath(work_dir)
    #        if cmd.startswith('/'):
    #            cmd = os.path.realpath(cmd)
    #        else:
    #            cmd = os.path.realpath(os.path.join(work_dir, cmd))
    #    else:
    #        if cmd.startswith('/'):
    #            work_dir = os.path.realpath(os.path.dirname(cmd))
    #            cmd = os.path.realpath(cmd)
    #        else:
    #            work_dir = os.path.realpath(os.curdir)
    #            cmd = os.path.realpath(os.path.join(work_dir, cmd))

    #    self.work_dir = work_dir
    #    self.cmd = cmd

    def set_status(self, status):
        self.status = status

    def run(self):
        work_dir = self.default_work_dir
        if self.jobspec.work_dir is not None:
            work_dir = self.jobspec.work_dir

        cmd = os.path.join(work_dir, self.jobspec.cmd)

        logging.info("Running '{}' with command '{}' in working dir '{}'".format(self, cmd, work_dir))

        p = subprocess.Popen(cmd,
                             cwd=work_dir,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=self.env)
        self.stdout, self.stderr = p.communicate(input)
        self.exit_code = p.returncode

    def to_dict(self):
        d = {
            'name': self.jobspec.name,
            'env': self.env,
            'id': self.id,
            'status': self.status,
            'exit_code': self.exit_code,
            'stdout': self.stdout,
            'stderr': self.stderr,
        }
        return d

    def __repr__(self):
        return "{}(id = {})".format(self.jobspec.name, self.id)
