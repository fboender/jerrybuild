import logging

from bottle import route, request, abort, template, static_file
import tools

@route('/static/<filename:path>')
def send_static(filename):
    """
    Serve static files.
    """
    return static_file(filename, root=tools.bin_rel_path('static/'))

@route('/')
def index():
    """
    Main landing page displays a list of jobs and their latest status.
    """
    jobdef_manager = request.deps['jobdef_manager']
    build_queue = request.deps['build_queue']
    jobdefs = jobdef_manager.get_jobdefs()

    job_status = {}
    for name, jobdef in jobdefs.items():
        jobdef_status = build_queue.get_latest_status(name)
        job_status[name] = jobdef_status

    return template('index.tpl', job_status=job_status)

@route('/job/definition/<job_name>')
def job_definition(job_name):
    """
    Display some information about a job's definition.
    """
    jobdef_manager = request.deps['jobdef_manager']
    build_queue = request.deps['build_queue']

    jobdef = jobdef_manager.get_jobdef(job_name)
    job_status = build_queue.get_latest_status(job_name)
    return template('job_definition.tpl', jobdef=jobdef, job_status=job_status)

@route('/job/status/<job_id>')
def job_status(job_id):
    """
    Show the job status for any job.
    """
    jobdef_manager = request.deps['jobdef_manager']
    build_queue = request.deps['build_queue']

    job_status = build_queue.get_job_status(job_id)
    job_name = job_status['jobdef_name']
    jobdef = jobdef_manager.get_jobdef(job_name)

    return template('job_status.tpl', jobdef=jobdef, job_status=job_status)

@route('/<:re:.*>', method=['GET', 'POST'])
def generic_handler():
    """
    The generic handler catches al requests not caught by any other route. It
    checks the configuration to see if the URL requested is one registered as a
    job's webhook URL handler. If so, it normalized the request and queues the
    job.

    It returns immediately (aynsc) with a JSON structure containing the job id.
    """
    jobdef_manager = request.deps['jobdef_manager']
    build_queue = request.deps['build_queue']
    config = request.deps['config']
    providers = request.deps['providers']

    jobdef = jobdef_manager.get_jobdef_from_url(request.path)
    if not jobdef:
        abort(404, "Not found")

    logging.info("Received event for job '{}'".format(jobdef.name))
    provider = providers[jobdef.provider]

    # Extract configuration options for this job definition from configuration
    # file.
    # FIXME: Shouldb't be here.
    config_section_name = jobdef.get_config_section_name()
    config_values = {}
    for option_key in config.options(config_section_name):
        option_value = config.get(config_section_name, option_key)
        config_values[option_key] = option_value

    # Put the headers of the request in the environment.
    env = {}
    for k, v in request.headers.items():
        env["HEADER_{}".format(k.upper())] = v
    env.update(provider.normalize(request, config_values))

    job = jobdef.make_job(request.body.read(), env)
    build_queue.put(job)

    return {'id': job.id}

