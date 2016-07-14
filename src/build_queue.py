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
from tools import mkdir_p, mail, listdir_sorted


class BuildQueue(threading.Thread):
    daemon = True

    def __init__(self, status_dir, smtp_server='127.0.0.1', server_url='http://localhost'):
        self.status_dir = status_dir
        self.jobs_dir = os.path.join(self.status_dir, 'jobs')
        self.all_dir = os.path.join(self.status_dir, 'jobs', '_all')
        self.make_status_dir()
        self.smtp_server = smtp_server
        self.server_url = server_url.rstrip('/')
        threading.Thread.__init__(self)
        self.queue = Queue.Queue()

    def run(self):
        self.handle_queue()

    def make_status_dir(self):
        mkdir_p(self.jobs_dir)
        mkdir_p(self.all_dir)

    def put(self, job):
        """
        Put a job in the queue for building.
        """
        job.set_status('queued')
        self.write_job_status(job)
        self.queue.put(job)
        logging.info("{}: queued".format(job))
        return job.id

    def handle_queue(self):
        """
        Continuously read the build queue for jobs and build them.
        """
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
        # Fetch the previously built job and set it on the job
        prev_job = self.get_latest_status(job.jobdef_name)
        if prev_job:
            job.set_prev_id(prev_job['id'])

        job.set_status('running')
        self.write_job_status(job, running=True)
        logging.info("{}: starting".format(job))

        for k, v in job.env.items():
            logging.debug('{}: env: {}={}'.format(job, k, v))
        logging.debug("{}: executing.".format(job))

        result = job.run()
        if result == -1:
            # Build was aborted. Remove the project specific job status, but
            # keep the _all job status so we can inspect the output if
            # required.
            job.set_status('aborted')
            logging.info("{}: intentionally aborted.".format(job))

            self.write_job_status(job, aborted=True)
        else:
            job.set_status('done')
            logging.info("{}: done. Exit code = {}".format(job, job.exit_code))

            if job.exit_code != 0:
                if job.mail_to:
                    # Send email
                    logging.info("{}: failed. Sending emails to {}".format(job, ', '.join(job.mail_to)))
                    self.send_fail_mail(job)
                    logging.info("{}: Emails sent".format(job))
                else:
                    logging.info("{}: No email configured. Not sending email.".format(job))

            self.write_job_status(job, running=False, latest=True)

    def write_job_status(self, job, running=False, latest=False, aborted=False):
        """
        Write the current job status as set in this object to job status dir
        and symlink them if needed.

        * Job status goes to state/_all/<uuid>.
        * Symlink goes from state/_all/<uuid> to state/<job_name>/uuid, unless
          aborted == True, in which case it is removed.
        * Symlink goes from FIXME
        """
        jobdef_dir = os.path.join(self.status_dir, 'jobs', job.jobdef_name)
        mkdir_p(jobdef_dir)  # If it doesn't exist yet
        job_status_path = os.path.join(self.all_dir, job.id)
        job_status_link = os.path.join(jobdef_dir, job.id)
        job_running_link = os.path.join(jobdef_dir, "running")
        job_latest_link = os.path.join(jobdef_dir, "latest")

        # Write the job status from the _all dir to the state/_all/<uuid> file
        status = job.to_dict()
        with open(job_status_path, 'w') as f:
            json.dump(status, f)

        # Link the job status from the _all dir to the state/<job_name>/<uuid>
        # file, unless the build was aborted.
        if not aborted:
            if not os.path.islink(job_status_link):
                os.symlink(os.path.join('..', '_all', job.id), job_status_link)
        else:
            logging.info("Removing status link")
            if os.path.islink(job_status_link):
                os.unlink(job_status_link)

        # Link or remove the state/<job_name>/running to the job file in _all
        if running:
            if os.path.islink(job_running_link):
                os.unlink(job_running_link)
            os.symlink(os.path.join('..', '_all', job.id), job_running_link)
        else:
            if os.path.islink(job_running_link):
                os.unlink(job_running_link)

        # Link the state/<job_name>/latest to the job file in _all
        if not aborted and latest:
            if os.path.islink(job_latest_link):
                os.unlink(job_latest_link)
            os.symlink(os.path.join('..', '_all', job.id), job_latest_link)

    def get_job_status_dir(self, jobdef_name):
        return os.path.join(self.status_dir, 'jobs', jobdef_name)

    def del_job_status(self, jobdef_name, job_id):
        jobdef_dir = self.get_job_status_dir(jobdef_name)
        os.unlink(os.path.join(jobdef_dir, job_id))
        os.unlink(os.path.join(jobdef_dir, '..', '_all', job_id))

    def get_job_status(self, job_id):
        job_status_path = os.path.join(self.all_dir, job_id)
        try:
            with open(job_status_path, 'r') as f:
                status = json.load(f)
            return status
        except IOError:
            return None

    def get_all_status(self, jobdef_name):
        """
        Return a list of all job statusses sorted by date (youngest first).
        """
        jobdef_dir = self.get_job_status_dir(jobdef_name)
        jobdef_dir = os.path.join(self.status_dir, 'jobs', jobdef_name)

        all_status = []
        try:
            for job_id in listdir_sorted(jobdef_dir, reverse=True):
                if job_id != "latest":
                    all_status.append(self.get_job_status(job_id))
        except OSError as err:
            # Surpress "not found" since the job may have never run.
            if err.errno != 2:
                raise
        return all_status

    def get_latest_status(self, jobdef_name):
        jobdef_dir = self.get_job_status_dir(jobdef_name)
        job_latest_link = os.path.join(jobdef_dir, "latest")
        try:
            with open(job_latest_link, 'r') as f:
                status = json.load(f)
            return status
        except IOError:
            return None

    def send_fail_mail(self, job):
        subject = "Build job '{}' (id={}..) failed with exit code {}'".format(job.jobdef_name.encode('utf8'),
                                                                              job.id[:8],
                                                                              job.exit_code)
        job_url = self.server_url + '/job/status/' + job.id
        msg = "Host = {}\n" \
              "Exit code = {}.\n\n" \
              "View the full job: {}.\n\n" \
              "OUTPUT\n======\n\n{}\n\n".format(socket.getfqdn(),
                                                job.exit_code,
                                                job_url,
                                                job.output.encode('utf8'))
        mail(job.mail_to, subject, msg, smtp_server=self.smtp_server)

