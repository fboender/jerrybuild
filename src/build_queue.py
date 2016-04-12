#!/usr/bin/python

import threading
import os
import logging
import Queue
import json
from tools import mkdir_p
from mail import mail


class BuildQueue(threading.Thread):
    daemon = True

    def __init__(self, status_dir, smtp_server='127.0.0.1'):
        self.status_dir = status_dir
        self.make_status_dir()
        self.smtp_server = smtp_server
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
            try:
                job = self.queue.get()
                self.build(job)
            except Exception as err:
                logging.exception(err)
                job.set_status("internal_error")
                self.write_job_status(job)

    def build(self, job):
        job.set_status('running')
        self.write_job_status(job)
        logging.info("{}: starting".format(job))

        for k, v in job.env.items():
            logging.debug('{}: env: {}={}'.format(job, k, v))
        logging.debug("{}: executing.".format(job))

        job.run()

        job.set_status('done')
        self.write_job_status(job, link_latest=True)
        logging.info("{}: done. Exit code = {}".format(job, job.exit_code))

        if job.exit_code != 0 and job.jobspec.mail_to:
            # Send email
            logging.info("{}: failed. Sending emails".format(job))
            logging.info("{}: failed. Sending emails to {}".format(job, ', '.join(job.jobspec.mail_to)))
            self.send_fail_mail(job)
            logging.info("{}: Emails sent".format(job))

    def write_job_status(self, job, link_latest=True):
        job_dir = os.path.join(self.status_dir, 'jobs')
        job_path = os.path.join(job_dir, job.id)
        project_dir = os.path.join(self.status_dir, 'projects', job.jobspec.name)
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

    def send_fail_mail(self, job):
        subject = "Build job '{}' for project '{}' failed with exit code {}'".format(job.id, job.jobspec.name, job.exit_code)
        msg = "Exit code = {}.\n\n" \
              "STDOUT\n======\n\n{}\n\n" \
              "STDERR\n======\n\n{}\n\n".format(job.exit_code, job.stdout, job.stderr)
        mail(job.mail_to, subject, msg)

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
