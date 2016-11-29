import logging
import time

from bottle import route, request, response, abort, template, static_file, redirect
import tools
import job

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

    job_statusses = {}
    for name, jobdef in jobdefs.items():
        jobdef_status = build_queue.get_latest_status(name)
        job_statusses[name] = jobdef_status

    return template('index.tpl', job_statusses=job_statusses)

@route('/job/<job_name>/definition')
def job_definition(job_name):
    """
    Display some information about a job's definition.
    """
    jobdef_manager = request.deps['jobdef_manager']
    build_queue = request.deps['build_queue']

    jobdef = jobdef_manager.get_jobdef(job_name)
    job_status = build_queue.get_latest_status(job_name)
    job_all_statusses = build_queue.get_all_status(job_name)

    return template('job_definition.tpl',jobdef=jobdef, job_status=job_status,
                    job_all_statusses=job_all_statusses)

@route('/job/<job_name>/shield')
def job_shield(job_name):
    """
    Show a build shield (http://shields.io/) for this job's latest build.
    """
    jobdef_manager = request.deps['jobdef_manager']
    build_queue = request.deps['build_queue']
    job_status = build_queue.get_latest_status(job_name)

    label = "build"
    status = "unknown"
    color = "lightgrey"

    if job_status is None:
        status = "never built"
    elif job_status.exit_code is None:
        status = "building"
        color = "blue"
    elif job_status.exit_code == 0:
        status = "passed"
        color = "brightgreen"
    else:
        status = "failed"
        color = "red"

    redirect('https://img.shields.io/badge/{}-{}-{}.svg'.format(label, status, color))

@route('/job/<job_id>/status')
def jobrun_status(job_id):
    """
    Show the job status for any job.
    """
    jobdef_manager = request.deps['jobdef_manager']
    build_queue = request.deps['build_queue']

    job_status = build_queue.get_job_status(job_id)
    job_name = job_status.jobdef_name
    jobdef = jobdef_manager.get_jobdef(job_name)

    return template('job_status.tpl', jobdef=jobdef, job_status=job_status)

@route('/job/<job_id>/rerun')
def jobrun_rerun(job_id):
    """
    Rerun an already executed job. We re-use the body and environment of the
    previous job.
    """
    build_queue = request.deps['build_queue']
    jobdef_manager = request.deps['jobdef_manager']

    job_status = build_queue.get_job_status(job_id)
    jobdef_name = job_status.jobdef_name
    jobdef = jobdef_manager.get_jobdef(jobdef_name)
    job = jobdef.make_job(job_status.body, job_status.env,
                          prev_id=job_status.id)

    new_job_id = build_queue.put(job)
    redirect("/job/{}/status".format(new_job_id))

@route('/job/<job_id>/stream_output')
def jobrun_stream_output(job_id):
    """
    Stream the output of a job to the browser. This is embedded in an iframe.
    If the job is still running, the output is streamed live. Otherwise, the
    collected output is sent.
    """
    yield u"<html><head><style>pre { padding: 10px; background-color:#000000; color:#FFFFFF; }</style></head><body><pre>"

    build_queue = request.deps['build_queue']
    if job_id in build_queue.running_jobs:
        # Job is running. Stream output as it's happening
        job_inst = build_queue.running_jobs[job_id]
        pos = 0
        while True:
            out = job_inst.output[pos:]
            if out:
                pos += len(out)
                yield out
            if job_inst.status != 'running':
                break
            time.sleep(0.1)
    else:
        # Job isn't running
        job_status = build_queue.get_job_status(job_id)
        yield job_status.output


@route('/<:re:.*>', method=['GET', 'POST'])
def generic_handler():
    """
    The generic handler catches all requests not caught by any other route. It
    checks the configuration to see if the URL requested is one registered as a
    job's webhook URL handler. If so, it normalizes the request and queues the
    job for building.

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

    # Log debug info about the received request
    logging.debug("request environ: {}".format(request.environ))
    logging.debug("request path: {}".format(request.path))
    logging.debug("request method: {}".format(request.method))
    for k, v in request.headers.items():
        logging.debug("request header: {}={}".format(k, v))
    for k, v in request.query.items():
        logging.debug("request query: {}={}".format(k, v))
    logging.debug("request body: {}".format(request.body.read()))
    logging.debug("request auth: {}".format(request.auth))

    # Put the headers of the request in the environment. Call the provider for
    # this job definition to handle additional tasks and update the environment
    # with its result.
    env = {}
    for k, v in request.headers.items():
        env["HEADER_{}".format(k.upper())] = v
    provider = providers[jobdef.provider]
    request_env = provider.normalize(request, jobdef)
    if request_env is False:
        # Normalization method aborted the request.
        return
    env.update(request_env)

    job_inst = jobdef.make_job(request.body.read().decode('utf8'), env)
    build_queue.put(job_inst)

    return {'id': job_inst.id}
