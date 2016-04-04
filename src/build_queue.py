#!/usr/bin/python

import threading
import os
import logging
import Queue
import uuid
import json
import subprocess
from tools import mkdir_p


class Job:
    def __init__(self, project, env, cmd, work_dir=None, id=None):
        self.project = project
        self.env = env
        self.set_cmd(cmd, work_dir)
        if id is not None:
            self.id = id
        else:
            self.id = uuid.uuid4().hex
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


class BuildQueue(threading.Thread):
    daemon = True

    def __init__(self, status_dir):
        self.status_dir = status_dir
        self.make_status_dir()
        threading.Thread.__init__(self)
        self.queue = Queue.Queue()

    def run(self):
        self.handle_queue()

    def make_status_dir(self):
        jobs_dir = os.path.join(self.status_dir, 'jobs')
        projects_dir = os.path.join(self.status_dir, 'projects')
        mkdir_p(jobs_dir)
        mkdir_p(projects_dir)

    def put(self, job):
        job.set_status('queued')
        self.write_job_status(job)
        self.queue.put(job)
        logging.info("{}: queued".format(job))
        return job.id

    def handle_queue(self):
        logging.info("Build queue running")
        while True:
            job = self.queue.get()
            self.build(job)

    def build(self, job):
        job.set_status('running')
        self.write_job_status(job)
        logging.info("{}: starting".format(job))

        for k, v in job.env.items():
            logging.debug('{}: env: {}={}'.format(job, k, v))
        logging.debug("{}: executing '{}'".format(job, job.cmd))

        job.run()

        job.set_status('done')
        self.write_job_status(job, link_latest=True)
        logging.info("{}: done. Exit code = {}".format(job, job.exit_code))

    def write_job_status(self, job, link_latest=False):
        job_dir = os.path.join(self.status_dir, 'jobs')
        job_path = os.path.join(job_dir, job.id)
        project_dir = os.path.join(self.status_dir, 'projects', job.project)
        project_path = os.path.join(project_dir, job.id)
        mkdir_p(project_dir)

        status = job.to_dict()
        with open(job_path, 'w') as f:
            json.dump(status, f)
        if not os.path.exists(project_path):
            os.symlink(job_path, project_path)

        if link_latest:
            latest_path = os.path.join(project_dir, 'latest')
            if os.path.exists(latest_path):
                os.unlink(latest_path)
            os.symlink(job_path, latest_path)

    def get_job_status(self, job_id):
        job_dir = os.path.join(self.status_dir, 'jobs')
        job_path = os.path.join(job_dir, job_id)
        try:
            with open(job_path, 'r') as f:
                status = json.load(f)
            return status
        except IOError:
            return None

    def get_project_status(self, project):
        project_dir = os.path.join(self.status_dir, 'projects', project)
        project_path = os.path.join(project_dir, 'latest')
        try:
            with open(project_path, 'r') as f:
                status = json.load(f)
            return status
        except IOError:
            return None
