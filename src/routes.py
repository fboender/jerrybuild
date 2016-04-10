import logging

from bottle import route, request, abort


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

@route('/<:re:.*>')
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
    env = provider.normalize(request, jobspec.name, config)
    job = jobspec_manager.make_job(jobspec.name, env)
    build_queue.put(job)
    return {'id': job.id}

