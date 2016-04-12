#!/usr/bin/python

import os
import logging
import uuid
import subprocess
import time


class Job:
    def __init__(self, jobspec, body, env, default_work_dir=None):
        self.jobspec = jobspec
        self.env = env
        self.env.update(self.jobspec.env)
        self.body = body
        self.id = uuid.uuid4().hex
        self.default_work_dir = default_work_dir
        self.status = None
        self.exit_code = None
        self.output = None
        self.time_start = None
        self.time_end = None

    def set_status(self, status):
        self.status = status

    def run(self):
        work_dir = self.default_work_dir
        if self.jobspec.work_dir is not None:
            work_dir = self.jobspec.work_dir

        cmd = os.path.join(work_dir, self.jobspec.cmd)

        logging.info("Running '{}' with command '{}' in working dir '{}'".format(self, cmd, work_dir))

        self.time_start = time.time()
        try:
            p = subprocess.Popen(cmd,
                                 cwd=work_dir,
                                 shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 env=self.env)
            self.output, ignore = p.communicate(self.body)
            self.exit_code = p.returncode
        except OSError as err:
            self.exit_code = 127
            self.output = str(err)
        self.time_end = time.time()

    def to_dict(self):
        d = {
            'name': self.jobspec.name,
            'env': self.env,
            'id': self.id,
            'status': self.status,
            'exit_code': self.exit_code,
            'output': self.output,
            'time_start': self.time_start,
            'time_end': self.time_end
        }
        return d

    def __repr__(self):
        return "{}(id = {})".format(self.jobspec.name, self.id)
