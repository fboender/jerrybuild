<%
reload_page = False
if job_status['status'] not in ('done', 'internal_error'):
    reload_page = True
end
%>
% rebase('base.tpl', title='Job', reload_page=reload_page)
% import tools
<main id="job-result">

% if job_status['status'] in ('done', 'internal_error'):
    <a href="/job/rerun/{{ job_status['id'] }}"><span class="action-button blue"><i class="fa fa-refresh" aria-hidden="true"></i> Rerun as new job</span></a>
% end

<h2><a href="/job/definition/{{ jobdef.name }}">{{ jobdef.name }}</a> ({{ job_status['id'] }})</h2>

<div class="job-status">
% include('helpers/job_status.tpl')
</div>

<table id="job-status-overview">
    <tr><th>ID</th><td>{{ job_status['id'] }}</td></tr>
    <tr><th>Status</th><td>{{ job_status['status'] }}</td></tr>
    <tr><th>Exit code</th><td>{{ job_status['exit_code'] }}</td></tr>
    <tr><th>Started</th><td>
        % include('helpers/job_time_start.tpl')
    </td></tr>
    <tr><th>Ended</th><td>
        % include('helpers/job_time_end.tpl')
    </td></tr>
    <tr><th>Built</th><td>
        % include('helpers/job_time_end_ago.tpl')
    </td></tr>
    <tr><th>Build time</th><td>
        % include('helpers/job_duration.tpl')
    </td></tr>
</table>

<h3>Environment</h3>
<table id="job-status-env">
    % for k, v in sorted(job_status['env'].items()):
        <tr>
            <th>{{ k }}</th>
            <td>{{ v }}</td>
        </tr>
    % end
</table>

<h3>Output</h3>
<pre>{{ job_status['output'] }}</pre>

</main>
