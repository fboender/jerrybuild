% rebase('base.tpl', title='Job specification')
% job_status_button = include('helpers/job_status.tpl')['job_status_button']
<main id="job-spec">

<div class="action-buttons">
% if job_status['status'] in ('done', 'internal_error'):
    <a href="/job/rerun/{{ job_status['id'] }}"><span class="action-button blue"><i class="fa fa-refresh" aria-hidden="true"></i> Rerun as new job</span></a>
% end
</div>

<h2>{{ jobdef.name }}</h2>
<p class="desc">{{ jobdef.desc }}</p>

<div class="job-status">
% if job_status is not None:
    % job_status_button(job_status['exit_code'], job_status['id'])
% else:
    <span class="button gray">Never run</span>
% end
</div>

<ul id="job-spec">
    <li><b>Name</b>: {{ jobdef.name }}</li>
    <li><b>URL</b>: {{ jobdef.url}}</li>
    <li><b>Provider</b>: {{ jobdef.provider }}</li>
    <li><b>Working dir</b>: {{ jobdef.work_dir }}</li>
    <li><b>Command</b>: {{ jobdef.cmd }}</li>
    <li><b>Failure mail to</b>: {{ ", ".join(jobdef.mail_to) }}</li>
</ul>
</main>
