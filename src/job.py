#!/usr/bin/python

import os
import logging
import uuid
import subprocess
import time
import socket
import copy
import sys


JOB_STATUSSES = [
    "queued",
    "running",
    "aborted",
    "done",
    "internal_error",
]

class Job:
    # NOTE: If you change the function definition, you also have to change
    # `to_dict` and `from_dict`!
    def __init__(self, jobdef_name, cmd, body, env, mail_to, work_dir=None,
                 prev_id=None):
        self.jobdef_name = jobdef_name
        self.cmd = cmd
        self.body = body
        self.env = env
        self.mail_to = list(mail_to)
        self.work_dir = work_dir
        self.status = None
        self.exit_code = None
        self.output = u''
        self.time_start = None
        self.time_end = None
        self.id = uuid.uuid4().hex
        self.prev_id = prev_id

    def set_status(self, status):
        assert status in JOB_STATUSSES
        self.status = status

    def set_prev_id(self, prev_id):
        self.prev_id = prev_id

    def run(self):
        """
        Run this job. Record the status in properties on this Job object.

        Returns -1 if the build was aborted (no error, but should continue
        building), 0 on success and 1 on failure.
        """
        work_dir = self.work_dir
        cmd = self.cmd
        env = os.environ.copy()
        env.update(self.env)
        bin_basedir = os.path.dirname(os.path.realpath(sys.argv[0]))
        tools_path = os.path.join(bin_basedir, 'tools')
        env["PATH"] = "{}:{}".format(env["PATH"], tools_path)

        logging.info("Running '{}' with command '{}' in working dir '{}'".format(self, cmd, work_dir))

        self.time_start = time.time()
        try:
            p = subprocess.Popen(cmd,
                                 cwd=work_dir,
                                 shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 env=env)

            # Stream output to self.output
            while True:
                stdout = p.stdout.readline().decode('utf8')
                if not stdout:
                    break
                self.output += stdout

            p.poll()
            self.exit_code = p.returncode
        except OSError as err:
            self.exit_code = 127
            self.output = str(err)

        self.time_end = time.time()

        if self.exit_code == 255:
            return -1
        elif self.exit_code == 0:
            return 0
        else:
            return 1

    def to_dict(self):
        d = {
            'jobdef_name': self.jobdef_name,
            'cmd': self.cmd,
            'body': self.body,
            'env': self.env,
            'mail_to': self.mail_to,
            'work_dir': self.work_dir,
            'status': self.status,
            'exit_code': self.exit_code,
            'output': self.output,
            'time_start': self.time_start,
            'time_end': self.time_end,
            'prev_id': self.prev_id,
            'id': self.id,
        }
        return d

    def __repr__(self):
        return "{}(id = {})".format(self.jobdef_name, self.id)


def from_dict(d):
    job = Job(d['jobdef_name'],
              d['cmd'],
              d['body'],
              d['env'],
              d['mail_to'],
              d['work_dir'])
    job.status = d['status']
    job.exit_code = d['exit_code']
    job.output = d['output']
    job.time_start = d['time_start']
    job.time_end = d['time_end']
    job.prev_id = d['prev_id']
    job.id = d['id']
    return job
