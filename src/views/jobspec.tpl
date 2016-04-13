% rebase('base.tpl', title='Job specification')
% job_status_button = include('helpers/job_status.tpl')['job_status_button']
<main id="job-spec">
<h2>{{ jobspec.name }}</h2>
<p class="desc">{{ jobspec.desc }}</p>

% if job_status is not None:
    % job_status_button(job_status['exit_code'], job_status['id'])
% else:
    <span class="button gray">Never run</span>
% end

<ul id="job-spec">
    <li><b>Name</b>: {{ jobspec.name }}</li>
    <li><b>URL</b>: {{ jobspec.url}}</li>
    <li><b>Provider</b>: {{ jobspec.provider }}</li>
    <li><b>Working dir</b>: {{ jobspec.work_dir }}</li>
    <li><b>Command</b>: {{ jobspec.cmd }}</li>
    <li><b>Failure mail to</b>: {{ ", ".join(jobspec.mail_to) }}</li>
</ul>
</main>
