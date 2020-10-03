"""
JobDefManager handles the loading of Job definitions from config file.
"""

import sys
import os
import logging

from . import jobdef
from . import tools


class JobDefManager:
    """
    The JobDefManager handles the loading of Job definitions from config file.
    Job definitions are used to create Job objects which represent a single
    build. Job definitions are kept as JobDef objects.
    """
    def __init__(self, config_file):
        self.jobdefs = {}
        self.config = None
        self.config_file = None
        self.default_work_dir = None
        self.log = logging.getLogger(__name__)
        self._load(config_file)

        if self.config is None or self.config_file is None:
            raise RuntimeError("JobDefs not initialized properly")

    def _load(self, config_file):
        """
        Load job definitions from `config_file`. This resets most of this
        object's state.
        """
        jobdefs = {}
        config = None
        config_file = config_file
        default_work_dir = os.path.realpath(os.path.dirname(sys.argv[0]))

        config = tools.config_load(config_file, case_sensitive=False)

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
        """
        Reload the job definitions from the config file.
        """
        self.log.info("Reloading configuration file")
        self._load(self.config_file)

    def get_jobdef(self, name):
        """
        Return the Job definition (JobDef object) corresponding to `name`.
        """
        return self.jobdefs[name]

    def get_jobdef_from_url(self, url):
        """
        Return the Job definition (JobDef object) that listens to `url`.
        """
        for jobdef_inst in self.jobdefs.values():
            if jobdef_inst.url.rstrip('/') == url.rstrip('/'):
                return jobdef_inst
        return None

    def get_jobdefs(self):
        """
        Return a dictionary of all job name => JobDef mappings.
        """
        return self.jobdefs
