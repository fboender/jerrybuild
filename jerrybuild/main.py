#!/usr/bin/env python
"""
Jerrybuild main
"""

import argparse
import logging
import signal
import socket

from . import bottle
from .bottle import request
from . import __METADATA__
from . import wsgi_server
from . import tools
from . import vacuum
from . import build_queue as bq
from . import routes  # noqa: F401
from .jobdef_manager import JobDefManager
from . import providers


class DepInjector:
    """
    Dependency injector plugin for the Bottle framework.
    """
    name = 'depinject'
    api = 2

    def __init__(self):
        self._deps = {}

    def add_dep(self, name, dep):
        self._deps[name] = dep

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            request.deps = self._deps
            body = callback(*args, **kwargs)
            return body
        return wrapper


def sig_hup_handler_generate(jobdef_manager):
    """
    Closure that returns a HUP signal handler that reloads the configuration
    file.
    """
    def sig_hup_handler(signum, frame):
        jobdef_manager.reload()
        bottle.TEMPLATES.clear()
    return sig_hup_handler


def job_changed_handler_generate(smtp_server, server_url, log):
    """
    Closure that returns a Job Changed handler. The Job Changed handler is
    called by the build queue whenever the job exit code changes from the
    previous build.
    """
    def job_changed_handler(cur_job, prev_job):
        """
        Send email if a job fails the first time or when it recovers (builds
        succesfully again).
        """
        if not cur_job.mail_to:
            log.info("Job %s status changed, but no emails configured. Not sending email", cur_job)
            return

        if cur_job.exit_code != 0 and \
           (prev_job is None or cur_job.exit_code != prev_job.exit_code):
            # Job failed and this is either the first time we've ran this job,
            # or the status changed from 'passed' to 'failed'.
            log.info("{}: failed. Sending emails to {}".format(cur_job, ', '.join(cur_job.mail_to)))
            subject = "Build job '{}' (id={}..) failed with exit code {}".format(cur_job.jobdef_name.encode('utf8'),
                                                                                 cur_job.id[:8],
                                                                                 cur_job.exit_code)
        elif (
            cur_job.exit_code == 0 and
            (
                prev_job is not None and
                cur_job.exit_code != prev_job.exit_code
            )
        ):
            # Job succeeded where it failed the previous time.
            log.info("{}: recovered. Sending emails to {}".format(cur_job, ', '.join(cur_job.mail_to)))
            subject = "Build job '{}' (id={}..) recovered".format(cur_job.jobdef_name.encode('utf8'),
                                                                  cur_job.id[:8],
                                                                  cur_job.exit_code)
        else:
            return

        job_url = server_url + '/job/status/' + cur_job.id
        msg = "Host = {}\n" \
              "Exit code = {}.\n\n" \
              "View the full job: {}.\n\n" \
              "OUTPUT\n======\n\n{}\n\n".format(socket.getfqdn(),
                                                cur_job.exit_code,
                                                job_url,
                                                cur_job.output.encode('utf8'))
        tools.mail(cur_job.mail_to, subject, msg, smtp_server=smtp_server)
        log.info("{}: Emails sent".format(cur_job))
    return job_changed_handler


def main():
    """
    Main method
    """
    parser = argparse.ArgumentParser(prog=__METADATA__["name"],
                                     description=__METADATA__["desc"])

    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {}'.format(__METADATA__["version"]))

    parser.add_argument('config',
                        metavar='CONFIG',
                        type=str,
                        help='Config file')

    args = parser.parse_args()

    # Load configuration
    config = tools.config_load(args.config)

    # Configure application logging
    loglevel = logging.INFO
    if config.has_option('server', 'log_level'):
        loglevel_str = config.get('server', 'log_level')
        loglevel_int = getattr(logging, loglevel_str.upper(), None)
        if not isinstance(loglevel_int, int):
            raise ValueError('Invalid log level: %s' % loglevel_str)
        loglevel = loglevel_int

    handler = logging.StreamHandler()
    fmt = '%(asctime)s %(levelname)8s %(name)s | %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    log = logging.getLogger(__package__)
    log.setLevel(loglevel)
    log.addHandler(handler)

    # Initialize the job changed handler, which will send an email when a job
    # failed. It's triggered by the job queue.
    status_dir = config.get('server', 'status_dir')
    smtp_server = '127.0.0.1'
    if config.has_option('server', 'smtp_server'):
        smtp_server = config.get('server', 'smtp_server')
    server_url = 'http://' + socket.getfqdn()
    if config.has_option('server', 'server_url'):
        server_url = config.get('server', 'server_url')
    job_changed_handler = job_changed_handler_generate(smtp_server, server_url, log)

    log.info("Initializing build queue")
    build_queue = bq.BuildQueue(status_dir, job_changed_handler)
    build_queue.start()

    log.info("Initializing job definition manager with config {}".format(args.config))
    jobdef_manager = JobDefManager(args.config)

    # The vacuumer will remove expired jobs.
    log.info("Initializing vacuumer")
    vacuumer = vacuum.Vacuum(jobdef_manager.get_jobdefs(), build_queue)
    vacuumer.verify_job_status()  # Handle invalid jobs
    vacuumer.start()

    # Setup a SIGHUP signal handler that reloads configuration
    signal.signal(signal.SIGHUP, sig_hup_handler_generate(jobdef_manager))

    # Set up dependency injections for the Bottle web routes.
    dep_inject = DepInjector()
    dep_inject.add_dep('build_queue', build_queue)
    dep_inject.add_dep('jobdef_manager', jobdef_manager)
    dep_inject.add_dep('config', config)
    dep_inject.add_dep('providers', providers.providers)

    bottle.TEMPLATE_PATH.insert(0, tools.data_path('views'))
    wsgiapp = bottle.default_app()
    wsgiapp.install(dep_inject)

    httpd_listen = '0.0.0.0'
    httpd_port = 5281
    if config.has_section('server'):
        if config.has_option('server', 'listen'):
            httpd_listen = config.get('server', 'listen')
        if config.has_option('server', 'port'):
            httpd_port = int(config.get('server', 'port'))

    log.info("Starting web server on {}:{}".format(httpd_listen, httpd_port))
    httpd = wsgi_server.WSGIServer(wsgiapp, listen=httpd_listen, port=httpd_port)
    log.info("Server listening on {}:{}".format(httpd_listen, httpd_port))
    httpd.serve_forever()


if __name__ == '__main__':
    main()
