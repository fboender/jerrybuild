import logging

from bottle import route, request, abort, template, static_file

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static/')

@route('/')
def index():
    jobspec_manager = request.deps['jobspec_manager']
    build_queue = request.deps['build_queue']
    jobspecs = jobspec_manager.get_jobspecs()

    job_status = {}
    for name, jobspec in jobspecs.items():
        jobspec_status = build_queue.get_project_status(name)
        job_status[name] = jobspec_status

    return template('index.tpl', job_status=job_status)

@route('/jobspec/<job_name>')
def jobspec(job_name):
    jobspec_manager = request.deps['jobspec_manager']
    build_queue = request.deps['build_queue']

    jobspec = jobspec_manager.get_jobspec(job_name)
    job_status = build_queue.get_project_status(job_name)
    return template('jobspec.tpl', jobspec=jobspec, job_status=job_status)

@route('/job/<job_id>')
def job(job_id):
    jobspec_manager = request.deps['jobspec_manager']
    build_queue = request.deps['build_queue']

    job_status = build_queue.get_job_status(job_id)
    job_name = job_status['name']
    jobspec = jobspec_manager.get_jobspec(job_name)

    return template('job.tpl', jobspec=jobspec, job_status=job_status)

@route('/status/project/<project>')
def status_project(project):
    build_queue = request.deps['build_queue']
    job_status = build_queue.get_project_status(project)
    if not job_status:
        abort(404, "No latest status found for project '{}'".format(project))
    return job_status

@route('/status/job/<job_id>')
def status_job(job_id):
    build_queue = request.deps['build_queue']
    job_status = build_queue.get_job_status(job_id)
    if not job_status:
        abort(404, "No job found with id '{}'".format(job_id))
    return job_status

@route('/<:re:.*>', method=['GET', 'POST'])
def generic_handler():
    jobspec_manager = request.deps['jobspec_manager']
    build_queue = request.deps['build_queue']
    config = request.deps['config']
    providers = request.deps['providers']

    jobspec = jobspec_manager.get_jobspec_from_url(request.path)
    if not jobspec:
        abort(404, "Not found")

    logging.info("Received event for project '{}'".format(jobspec.name))
    provider = providers[jobspec.provider]

    env = {}
    for k, v in request.headers.items():
        env["HEADER_{}".format(k.upper())] = v
    env.update(provider.normalize(request, jobspec.name, config))

    job = jobspec_manager.make_job(jobspec.name, request.body.read(), env)
    build_queue.put(job)
    return {'id': job.id}

