#!/usr/bin/python

import os
import logging
import uuid
import subprocess
import time

JOB_STATUSSES = [
    "queued",
    "running",
    "done",
    "internal_error"
]

class Job:
    def __init__(self, jobdef_name, cmd, body, env, work_dir=None):
        self.jobdef_name = jobdef_name
        self.cmd = cmd
        self.body = body
        self.env = env
        self.work_dir = work_dir
        self.status = None
        self.exit_code = None
        self.output = None
        self.time_start = None
        self.time_end = None
        self.id = uuid.uuid4().hex

    def set_status(self, status):
        assert status in JOB_STATUSSES
        self.status = status

    def run(self):
        work_dir = self.work_dir

        cmd = os.path.join(work_dir, self.cmd)

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
            'jobdef_name': self.jobdef_name,
            'cmd': self.cmd,
            'body': self.body,
            'env': self.env,
            'status': self.status,
            'exit_code': self.exit_code,
            'output': self.output,
            'time_start': self.time_start,
            'time_end': self.time_end,
            'id': self.id,
        }
        return d

    def send_fail_mail(self, job):
        subject = "Build job '{}' (id={}..) failed with exit code {}'".format(self.jobdef_name, self.id[:8], self.exit_code)
        msg = "Host = {}\n" \
              "Exit code = {}.\n\n" \
              "OUTPUT\n======\n\n{}\n\n".format(socket.getfqdn(), self.exit_code, self.output)
        mail(job.mail_to, subject, msg)

    def __repr__(self):
        return "{}(id = {})".format(self.jobdef_name, self.id)
