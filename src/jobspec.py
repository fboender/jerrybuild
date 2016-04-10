#!/usr/bin/python

class JobSpec:
    def __init__(self, name, url, provider, cmd, work_dir=None, mail_to=[], custom_params={}):
        self.name = name
        self.url = url
        self.provider = provider
        self.cmd = cmd
        self.work_dir = work_dir
        self.mail_to = mail_to
        self.custom_params = custom_params

    def __repr__(self):
        return "JobSpec <name={}>".format(self.name)


def from_config(config, section_name):
    params = {
        'name': section_name.split(':', 1)[1],
        'url': None,
        'provider': 'generic',
        'cmd': None,
        'work_dir': None,
        'mail_to': [],
        'custom_params': {},
    }

    for option in config.options(section_name):
        if option == 'url':
            params['url'] = config.get(section_name, 'url')
        elif option == 'provider':
            params['provider'] = config.get(section_name, 'provider')
        elif option == 'cmd':
            params['cmd'] = config.get(section_name, 'cmd')
        elif option == 'work_dir':
            params['work_dir'] = config.get(section_name, 'work_dir')
        elif option == 'mail_to':
            params['mail_to'] = [s.strip() for s in config.get(section_name, 'mail_to').split(',')]
        else:
            params['custom_params'][option] = config.get(section_name, option)

    for required in ['url', 'cmd']:
        if params[required] is None:
            raise KeyError("Missing required option '{}' in '{}'".format(required, section_name))

    return JobSpec(**params)
