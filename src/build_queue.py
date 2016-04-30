#!/usr/bin/python

import threading
import os
import logging
import sys
import json
import socket
if sys.version_info.major > 2:
    import queue as Queue
else:
    import Queue
from tools import mkdir_p, mail


class BuildQueue(threading.Thread):
    daemon = True

    def __init__(self, status_dir, smtp_server='127.0.0.1'):
        self.status_dir = status_dir
        self.jobs_dir = os.path.join(self.status_dir, 'jobs')
        self.all_dir = os.path.join(self.status_dir, 'jobs', '_all')
        self.make_status_dir()
        self.smtp_server = smtp_server
        threading.Thread.__init__(self)
        self.queue = Queue.Queue()

    def run(self):
        self.handle_queue()

    def make_status_dir(self):
        mkdir_p(self.jobs_dir)
        mkdir_p(self.all_dir)

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
        self.write_job_status(job)
        logging.info("{}: done. Exit code = {}".format(job, job.exit_code))

        if job.exit_code != 0:
            if job.mail_to:
                # Send email
                logging.info("{}: failed. Sending emails to {}".format(job, ', '.join(job.mail_to)))
                job.send_fail_mail(job)
                logging.info("{}: Emails sent".format(job))
            else:
                logging.info("{}: No email configured. Not sending email.".format(job))

    def write_job_status(self, job):
        jobdef_dir = os.path.join(self.status_dir, 'jobs', job.jobdef_name)
        mkdir_p(jobdef_dir)  # If it doesn't exist yet
        job_status_path = os.path.join(self.all_dir, job.id)
        job_status_link = os.path.join(jobdef_dir, job.id)
        job_latest_link = os.path.join(jobdef_dir, "latest")

        status = job.to_dict()
        with open(job_status_path, 'w') as f:
            json.dump(status, f)

        if not os.path.exists(job_status_link):
            os.symlink(job_status_path, job_status_link)

        if os.path.exists(job_latest_link):
            os.unlink(job_latest_link)
        os.symlink(job_status_path, job_latest_link)

    def get_job_status(self, job_id):
        job_status_path = os.path.join(self.all_dir, job_id)
        try:
            with open(job_status_path, 'r') as f:
                status = json.load(f)
            return status
        except IOError:
            return None

    def get_latest_status(self, jobdef_name):
        jobdef_dir = os.path.join(self.status_dir, 'jobs', jobdef_name)
        job_latest_link = os.path.join(jobdef_dir, "latest")
        try:
            with open(job_latest_link, 'r') as f:
                status = json.load(f)
            return status
        except IOError:
            return None
