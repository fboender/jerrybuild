% rebase('base.tpl', title='Job specification')
<main id="job-spec">
<h2>{{ jobspec.name }}</h2>

% if job_status is not None:
    % if job_status['exit_code'] == 0:
        <a href="/job/{{ job_status['id'] }}"><span class="button green">Passed</span></a>
    % else:
        <a href="/job/{{ job_status['id'] }}"><span class="button red">Failed`</span></a>
    % end
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
