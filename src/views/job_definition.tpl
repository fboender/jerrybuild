% rebase('base.tpl', title='Job specification')
<main id="job-spec">

<div class="action-buttons">
% if job_status and job_status['status'] in ('done', 'internal_error'):
    <a href="/job/{{ job_status['id'] }}/rerun"><span class="action-button blue"><i class="fa fa-refresh" aria-hidden="true"></i> Rerun as new job</span></a>
% end
</div>

<h2>{{ jobdef.name }}</h2>
<p class="desc">{{ jobdef.desc }}</p>

<div class="job-status">
% include('helpers/job_status.tpl')
</div>

<ul id="job-spec">
    <li><b>Name</b>: {{ jobdef.name }}</li>
    <li><b>URL</b>: {{ jobdef.url}}</li>
    <li><b>Provider</b>: {{ jobdef.provider }}</li>
    <li><b>Working dir</b>: {{ jobdef.work_dir }}</li>
    <li><b>Command</b>: {{ jobdef.cmd }}</li>
    <li><b>Failure mail to</b>: {{ ", ".join(jobdef.mail_to) }}</li>
</ul>

<h3>Shield</h3>
<a href="/job/{{ jobdef.name }}/shield"><img src="/job/{{ jobdef.name }}/shield" /></a>
</main>
