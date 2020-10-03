"""
Job definition objects contain all the information required to create jobs.
"""

from .job import Job
from . import tools


class JobDef:
    """
    Job definition objects contain all the information required to create jobs.
    JobDef objects are generally constructed through `from_config()` by the
    JobDefManager. JobDef objects can be used to create jobs using make_job().
    """
    # NOTE: If you change the function definition, you also have to change
    # `from_config`!
    def __init__(self, name, desc, url, provider, cmd, env, work_dir=None,
                 keep_jobs=0, mail_to=None, pass_query=False, clean_env=True,
                 custom_params=None):
        self.name = name
        self.desc = desc
        self.url = url
        self.provider = provider
        self.cmd = cmd
        self.env = env
        self.work_dir = work_dir
        self.keep_jobs = keep_jobs
        self.mail_to = []
        if mail_to is not None:
            self.mail_to = mail_to
        self.pass_query = pass_query
        self.clean_env = clean_env
        self.custom_params = {}
        if custom_params is not None:
            self.custom_params = custom_params

    def make_job(self, body, env, prev_id=None):
        """
        Create a new job from this job defimition.
        """
        newenv = {}
        newenv.update(self.env.items())
        newenv.update(env.items())
        newenv.update(self.custom_params.items())

        job = Job(self.name, self.cmd, body, newenv, self.mail_to,
                  self.work_dir, prev_id=prev_id)
        return job

    def __repr__(self):
        return "JobDef <name={}>".format(self.name)


def from_config(config, section_name):
    """
    Generate a JobDef instance from a configuration section.
    """
    params = {
        'name': section_name.split(':', 1)[1],
        'desc': "No description",
        'url': None,
        'provider': 'generic',
        'cmd': None,
        'env': {},
        'work_dir': None,
        'keep_jobs': 0,
        'mail_to': set(),
        'pass_query': False,
        'clean_env': True,
        'custom_params': {},
    }

    # Global settings. Are overridden by job specific settings
    for option in config.options('server'):
        if option == 'mail_to':
            mail_tos = [mail_to.strip() for mail_to in config.get('server', 'mail_to').split(',')]
            params['mail_to'].update(mail_tos)
        elif option == 'work_dir':
            params['work_dir'] = config.get('server', 'work_dir')
        elif option == 'keep_jobs':
            params['keep_jobs'] = config.get('server', 'keep_jobs')
        elif option.startswith('env_'):
            env_name = option[4:].strip()
            env_value = config.get('server', option).strip()
            params['env'][env_name] = env_value

    # Job specific settings.
    for option in config.options(section_name):
        if option == 'desc':
            params['desc'] = config.get(section_name, 'desc')
        elif option == 'url':
            params['url'] = config.get(section_name, 'url')
        elif option == 'provider':
            params['provider'] = config.get(section_name, 'provider')
        elif option == 'cmd':
            params['cmd'] = config.get(section_name, 'cmd')
        elif option == 'work_dir':
            params['work_dir'] = config.get(section_name, 'work_dir')
        elif option == 'keep_jobs':
            params['keep_jobs'] = config.get(section_name, 'keep_jobs')
        elif option == 'mail_to':
            params['mail_to'].update([s.strip() for s in config.get(section_name, 'mail_to').split(',')])
        elif option == 'pass_query':
            params['pass_query'] = tools.to_bool(config.get(section_name, 'pass_query'))
        elif option == 'clean_env':
            params['clean_env'] = tools.to_bool(config.get(section_name, 'clean_env'))
        elif option.startswith('env_'):
            env_name = option[4:].strip()
            env_value = config.get(section_name, option).strip()
            params['env'][env_name] = env_value
        else:
            params['custom_params'][option] = config.get(section_name, option)

    for required in ['url', 'cmd']:
        if params[required] is None:
            raise KeyError("Missing required option '{}' in '{}'".format(required, section_name))

    return JobDef(**params)
