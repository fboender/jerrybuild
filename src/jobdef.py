#!/usr/bin/python

from job import Job

class JobDef:
    def __init__(self, name, desc, url, provider, cmd, env, work_dir=None,
                 mail_to=[], custom_params={}):
        self.name = name
        self.desc = desc
        self.url = url
        self.provider = provider
        self.cmd = cmd
        self.env = env
        self.work_dir = work_dir
        self.mail_to = mail_to
        self.custom_params = custom_params

    def get_config_section_name(self):
        return 'job:{}'.format(self.name)

    def make_job(self, body, env):
        job = Job(self.name, self.cmd, body, env, self.mail_to, self.work_dir)
        return job

    def __repr__(self):
        return "JobDef <name={}>".format(self.name)


def from_config(config, section_name):
    params = {
        'name': section_name.split(':', 1)[1],
        'desc': "No description",
        'url': None,
        'provider': 'generic',
        'cmd': None,
        'env': {},
        'work_dir': None,
        'mail_to': set(),
        'custom_params': {},
    }

    for option in config.options('server'):
        if option == 'mail_to':
            mail_tos = [mail_to.strip() for mail_to in config.get('server', 'mail_to').split(',')]
            params['mail_to'].update(mail_tos)
        elif option.startswith('env_'):
            env_name = option[4:].strip()
            env_value = config.get('server', option).strip()
            params['env'][env_name] = env_value

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
        elif option == 'mail_to':
            params['mail_to'].update([s.strip() for s in config.get(section_name, 'mail_to').split(',')])
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
