#!/usr/bin/python

import sys
import os
import ConfigParser

import jobspec
from job import Job


class JobSpecManager:
    def __init__(self, config_file):
        self.jobspecs = {}
        self.config = None
        self.config_file = None
        self.default_work_dir = None
        self.load(config_file)

        if self.config is None or self.config_file is None:
            raise RuntimeError("Jobspecs not initialized properly")

    def load(self, config_file):
        jobspecs = {}
        config = None
        config_file = config_file
        default_work_dir = os.path.realpath(os.path.dirname(sys.argv[0]))

        config = ConfigParser.RawConfigParser()
        config.read(config_file)

        if config.has_option('server', 'work_dir'):
            default_work_dir = config.get('server', 'work_dir')

        jobspecs = {}
        for section_name in config.sections():
            if section_name.startswith('project:'):
                name = section_name.split(':', 1)[1]
                jobspecs[name] = jobspec.from_config(config, section_name)

        self.jobspecs = jobspecs
        self.config = config
        self.config_file = config_file
        self.default_work_dir = default_work_dir

    def get_jobspec(self, name):
        return self.jobspecs[name]

    def get_jobspec_from_url(self, url):
        for name, jobspec_inst in self.jobspecs.items():
            if jobspec_inst.url.rstrip('/') == url.rstrip('/'):
                return jobspec_inst
        return None

    def get_jobspecs(self):
        return self.jobspecs

    def make_job(self, name, body, env):
        jobspec = self.jobspecs[name]
        job = Job(jobspec, body, env, default_work_dir=self.default_work_dir)
        return job
