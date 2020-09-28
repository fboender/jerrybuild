% rebase('base.tpl', title='Job specification')
<main id="job-spec">

<div class="action-buttons">
% if job_status and job_status.status == 'done':
    <a href="/job/{{ job_status.id }}/rerun"><span class="action-button blue"><i class="fa fa-refresh" aria-hidden="true"></i> Rerun as new job</span></a>
% end
</div>

<h2>{{ jobdef.name }}</h2>
<div class="job-spec">
<p class="desc">{{ jobdef.desc }}</p>

<table id="job-spec">
    <tr><th><b>Name:</b></th><td> {{ jobdef.name }}</td></tr>
    <tr><th><b>URL:</b></th><td> {{ jobdef.url}}</td></tr>
    <tr><th><b>Provider:</b></th><td> {{ jobdef.provider }}</td></tr>
    <tr><th><b>Working dir:</b></th><td> {{ jobdef.work_dir }}</td></tr>
    <tr><th><b>Command:</b></th><td> {{ jobdef.cmd }}</td></tr>
    <tr><th><b>Failure mail to:</b></th><td> {{ ", ".join(jobdef.mail_to) }}</td></tr>
</table>
</div>


<div class="status-history">
<h3>Status history</h3>
<table>
% if len(job_all_statusses) == 0:
    <tr>
        <td colspan="2">Never built</td>
    </tr>
% else:
    % for job_status in job_all_statusses:
        <tr>
            <td>
            % include('helpers/job_status.tpl')
            </td>
            <td>
            % include('helpers/job_time_end_ago.tpl')
            </td>
        </tr>
    % end
% end
</table>
</div>

<h3>Shield</h3>
<a href="/job/{{ jobdef.name }}/shield"><img src="/job/{{ jobdef.name }}/shield" /></a>
</main>
