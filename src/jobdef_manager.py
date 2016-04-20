#!/usr/bin/python

import sys
import os
import ConfigParser
import logging

import jobdef
from job import Job


class JobDefManager:
    def __init__(self, config_file):
        self.jobdefs= {}
        self.config = None
        self.config_file = None
        self.default_work_dir = None
        self.load(config_file)

        if self.config is None or self.config_file is None:
            raise RuntimeError("JobDefs not initialized properly")

    def load(self, config_file):
        jobdefs = {}
        config = None
        config_file = config_file
        default_work_dir = os.path.realpath(os.path.dirname(sys.argv[0]))

        config = ConfigParser.RawConfigParser()
        config.optionxform = str  # Case-sensitive option names for env_
        config.read(config_file)

        if config.has_option('server', 'work_dir'):
            default_work_dir = config.get('server', 'work_dir')

        jobdefs = {}
        for section_name in config.sections():
            if section_name.startswith('job:'):
                name = section_name.split(':', 1)[1]
                jobdefs[name] = jobdef.from_config(config, section_name)

        self.jobdefs = jobdefs
        self.config = config
        self.config_file = config_file
        self.default_work_dir = default_work_dir

    def reload(self):
        logging.info("Reloading configuration file")
        self.load(self.config_file)

    def get_jobdef(self, name):
        return self.jobdefs[name]

    def get_jobdef_from_url(self, url):
        for name, jobdef_inst in self.jobdefs.items():
            if jobdef_inst.url.rstrip('/') == url.rstrip('/'):
                return jobdef_inst
        return None

    def get_jobdefs(self):
        return self.jobdefs

    def make_job(self, name, body, env):
        jobdef = self.jobdefs[name]
        cmd = jobdef.cmd
        job = Job(name, cmd, body, env, jobdef.mail_to, work_dir=self.default_work_dir)
        return job
