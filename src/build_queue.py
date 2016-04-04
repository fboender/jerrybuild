#!/usr/bin/python

import threading
import os
import logging
import Queue
import uuid
import json
import subprocess
from tools import mkdir_p


class BuildQueue(threading.Thread):
    daemon = True

    def __init__(self, status_dir):
        self.status_dir = status_dir
        self.make_status_dir()
        threading.Thread.__init__(self)
        self.queue = Queue.Queue()

    def make_status_dir(self):
        jobs_dir = os.path.join(self.status_dir, 'jobs')
        projects_dir = os.path.join(self.status_dir, 'projects')
        mkdir_p(jobs_dir)
        mkdir_p(projects_dir)

    def run(self):
        logging.info("Build queue running")
        while True:
            job = self.queue.get()
            self.build(job)

    def put(self, project, env, cmd, work_dir=None):
        job = {
            'project': project,
            'id': uuid.uuid4().hex,
            'env': env,
            'cmd': cmd,
            'work_dir': work_dir,
        }
        self.write_job_status(job, 'queued')
        self.queue.put(job)
        return job['id']

    def build(self, job):
        self.write_job_status(job, 'starting')

        job_id = job['id']

        logging.info("job {}: starting".format(job_id))
        for k, v in job['env'].items():
            logging.debug('job {}: env: {}={}'.format(job_id, k, v))
        logging.debug("job {}: executing '{}'".format(job_id, job['cmd']))

        self.write_job_status(job, 'building')

        if job['work_dir'] is not None:
            cwd = os.path.realpath(job['work_dir'])
            if job['cmd'].startswith('/'):
                cmd = os.path.realpath(job['cmd'])
            else:
                cmd = os.path.realpath(os.path.join(cwd, job['cmd']))
        else:
            if job['cmd'].startswith('/'):
                cwd = os.path.realpath(os.path.dirname(job['cmd']))
                cmd = os.path.realpath(job['cmd'])
            else:
                cwd = os.path.realpath(os.curdir)
                cmd = os.path.realpath(os.path.join(cwd, job['cmd']))

        print cwd, cmd

        p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=job['env'])
        stdout, stderr = p.communicate(input)
        self.write_job_status(job, 'finished', exit_code=p.returncode,
                              stdout=stdout, stderr=stderr)
        logging.info("job {}: done. Exit code: {}".format(job_id, p.returncode))

        job_dir = os.path.join(self.status_dir, 'jobs')
        job_path = os.path.join(job_dir, job['id'])
        project_dir = os.path.join(self.status_dir, 'projects', job['project'])
        latest_path = os.path.join(project_dir, 'latest')
        try:
            os.unlink(latest_path)
        except OSError:
            pass
        os.symlink(job_path, latest_path)

    def write_job_status(self, job, status, exit_code=None, stdout=None, stderr=None):
        job_dir = os.path.join(self.status_dir, 'jobs')
        job_path = os.path.join(job_dir, job['id'])
        project_dir = os.path.join(self.status_dir, 'projects', job['project'])
        project_path = os.path.join(project_dir, job['id'])
        mkdir_p(project_dir)

        status = {
            'project': job['project'],
            'job_id': job['id'],
            'status': status,
            'exit_code': exit_code,
            'stdout': stdout,
            'stderr': stderr,
        }
        with open(job_path, 'w') as f:
            json.dump(status, f)
        if not os.path.exists(project_path):
            os.symlink(job_path, project_path)

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
