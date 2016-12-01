#!/usr/bin/python

import threading
import os
import logging
import sys
import json
if sys.version_info.major > 2:
    import queue as Queue
else:
    import Queue
from tools import mkdir_p, listdir_sorted
import job


class BuildQueue(threading.Thread):
    """
    The BuildQueue object manages pending and running build jobs. It also
    handles writing the job status to disk. New jobs can be put on the queue
    using `put()`.
    """
    daemon = True

    def __init__(self, status_dir, job_changed_handler=None):
        threading.Thread.__init__(self)
        self.status_dir = status_dir
        self.job_changed_handler = job_changed_handler
        self.jobs_dir = os.path.join(self.status_dir, 'jobs')
        self.all_dir = os.path.join(self.status_dir, 'jobs', '_all')
        self._make_status_dir()
        self.queue = Queue.Queue()
        self.running_jobs = {}

    def run(self):
        self._handle_queue()

    def _make_status_dir(self):
        mkdir_p(self.jobs_dir)
        mkdir_p(self.all_dir)

    def put(self, job):
        """
        Put a job in the queue for building.
        """
        # Fetch the previously built job and set it on the job. This is used
        # for linking and comparing to the previous job.
        prev_job = self.get_latest_status(job.jobdef_name)
        if prev_job:
            job.set_prev_id(prev_job.id)

        job.set_status('queued')
        self._write_job_status(job)
        self.queue.put(job)
        logging.info("{}: queued".format(job))
        return job.id

    def _handle_queue(self):
        """
        Continuously read the build queue for jobs and build them.
        """
        logging.info("Build queue running")
        while True:
            job = self.queue.get()
            self._build(job)

    def _build(self, job):
        self.running_jobs[job.id] = job

        job.set_status('running')
        self._write_job_status(job)
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
            logging.info("{}: result: intentionally aborted. Exit code = {}".format(job, job.exit_code))

            self._write_job_status(job, aborted=True)
        else:
            job.set_status('done')
            if job.exit_code == 0:
                logging.info("{}: result: success. Exit code = {}".format(job, job.exit_code))
            else:
                logging.warn("{}: result: failed. Exit code = {}".format(job, job.exit_code))

            self._write_job_status(job)

            prev_job = self.get_job_status(job.prev_id)
            if (prev_job is not None and job.exit_code != prev_job.exit_code):
                # Job result has changed since last time. Call the `job_changed_handler`.
                if self.job_changed_handler is not None:
                    logging.debug("{}: status changed. Calling the 'job changed' handler".format(job.id[:8]))
                    self.job_changed_handler(job, prev_job)
                else:
                    logging.debug("{}: status changed, but no 'job changed' handler defined.".format(job.id[:8]))

        del self.running_jobs[job.id]

    def _write_job_status(self, job, aborted=False):
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

    def get_job_status_dir(self, jobdef_name):
        return os.path.join(self.status_dir, 'jobs', jobdef_name)

    def del_job_status(self, jobdef_name, job_id):
        jobdef_dir = self.get_job_status_dir(jobdef_name)
        os.unlink(os.path.join(jobdef_dir, job_id))
        os.unlink(os.path.join(jobdef_dir, '..', '_all', job_id))

    def get_job_status(self, job_id):
        if job_id is None:
            return None

        job_status_path = os.path.join(self.all_dir, job_id)
        try:
            with open(job_status_path, 'r') as f:
                status = json.load(f)
            return job.from_dict(status)
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
                all_status.append(self.get_job_status(job_id))
        except OSError as err:
            # Surpress "not found" since the job may have never run.
            if err.errno != 2:
                raise
        return all_status

    def get_latest_status(self, jobdef_name):
        all_status = self.get_all_status(jobdef_name)
        try:
            latest_status = all_status[0]
            return latest_status
        except IndexError:
            return None
