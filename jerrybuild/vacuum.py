import threading
import os
import logging
import time


class Vacuum(threading.Thread):
    daemon = True

    def __init__(self, jobdefs, build_queue, vacuum_interval=3600):
        threading.Thread.__init__(self)
        self.jobdefs = jobdefs
        self.build_queue = build_queue
        self.vacuum_interval = vacuum_interval
        self.log = logging.getLogger(__name__)

    def verify_job_status(self):
        """
        Go through all the job statusses and handle any invalid ones. Jobs can
        become invalid if, for example, Jerrybuild is killed.
        """
        for jobdef_name, jobdef in self.jobdefs.items():
            job_statusses = self.build_queue.get_all_status(jobdef_name)
            for job in job_statusses:
                if job.status in ['queued', 'running']:
                    job.status = 'aborted'
                    self.build_queue._write_job_status(job, aborted=True)

    def run(self):
        self.log.info('Vacuum running')
        try:
            while True:
                time.sleep(self.vacuum_interval)
                self._do_vacuum()
        except Exception as err:
            self.log.exception("Vacuum stopped unexpectantly: {}".format(err))

    def _do_vacuum(self):
        for jobdef_name, jobdef in self.jobdefs.items():
            if jobdef.keep_jobs == 0 or jobdef.keep_jobs == '0':
                # Don't vacuum at all
                continue
            self.log.debug("Vacuuming job {}".format(jobdef_name))
            job_status_dir = self.build_queue.get_job_status_dir(jobdef_name)
            filter_func = self._get_dir_filter(jobdef.keep_jobs)
            remove_job_ids = filter_func(job_status_dir, jobdef.keep_jobs)
            self.log.debug("Removing {} job outputs for job '{}'".format(len(remove_job_ids), jobdef_name))
            for job_id in remove_job_ids:
                self.build_queue.del_job_status(jobdef_name, job_id)

    def _get_dir_filter(self, keep_jobs):
        try:
            int(keep_jobs)
            return dir_filter_nr
        except ValueError:
            return dir_filter_days


def dir_filter_nr(job_status_dir, keep_jobs):
    """
    Return a list of job ID's that should be removed from the job status
    directory. Keeps the last `keep_jobs` nr of jobs (latest not included)
    """
    keep_nr = int(keep_jobs)

    file_mtimes = []
    for fname in os.listdir(job_status_dir):
        if len(fname) != 32:
            # Skip any files that are not UUIDs.
            continue

        ftime = os.stat(os.path.join(job_status_dir, fname)).st_mtime
        file_mtimes.append((ftime, fname))

    return [file_mtime[1] for file_mtime in sorted(file_mtimes)[:-keep_nr]]


def dir_filter_days(job_status_dir, keep_jobs):
    """
    Return a list of job ID's that should be removed from the job status
    directory. Keeps the jobs that are younger than `keep_jobs` days. (latest
    not included)
    """
    keep_days = int(keep_jobs.rstrip(' d'))

    now = time.time()
    files = []
    for fname in os.listdir(job_status_dir):
        if len(fname) == 32:
            # Skip any files that are not UUIDs.
            continue

        ftime = os.stat(os.path.join(job_status_dir, fname)).st_mtime
        if ((now - ftime) / 86400) > keep_days:
            files.append(fname)

    return files
