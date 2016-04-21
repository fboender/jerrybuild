#!/usr/bin/python

import logging
import sys
import unittest

sys.path.insert(0, '../src')
from jobdef_manager import JobDefManager

class ConfigTestCase(unittest.TestCase):
    """
    Test whether the configuration values are properly picked up by various
    parts of Jerrybuild.
    """
    def testJobEmailFrom(self):
        """
        Ensure both [server] and [job:] mail_to addresses are included in the
        job.
        """
        jobdef_manager = JobDefManager('test.cfg')
        jobdef = jobdef_manager.get_jobdef('test')
        job = jobdef.make_job('', {})
        self.assertIn('global_1@example.com', job.mail_to)
        self.assertIn('global_2@example.com', job.mail_to)
        self.assertIn('local_1@example.com', job.mail_to)
        self.assertIn('local_2@example.com', job.mail_to)

    def testJobGlobalWorkdir(self):
        """
        Ensure that a job with no work_dir gets the global work_dir.
        """
        jobdef_manager = JobDefManager('test.cfg')
        jobdef = jobdef_manager.get_jobdef('test')
        job = jobdef.make_job('', {})
        self.assertEquals(job.work_dir, '/var/lib/jerrybuild/workspace')

    def testJobdefLocalWorkdir(self):
        """
        Ensure that a job definition with a work_dir gets the local work_dir.
        """
        jobdef_manager = JobDefManager('test.cfg')
        jobdef = jobdef_manager.get_jobdef('test_local_workdir')
        job = jobdef.make_job('', {})
        self.assertEquals(job.work_dir, '/opt/build')


if __name__ == '__main__':
    logging.basicConfig(level=logging.FATAL,
                        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
                        filename='test.log',
                        filemode='a')
    unittest.main(exit=True)
