% rebase('base.tpl', title='Job')
% import datetime
% import time
% import duration
<%
time_start_str = time.strftime("%Y-%m-%dT%H:%M:%S", datetime.datetime.fromtimestamp(job_status['time_start']).timetuple())
time_end_str = time.strftime("%Y-%m-%dT%H:%M:%S", datetime.datetime.fromtimestamp(job_status['time_end']).timetuple())
%>
<main id="job-result">
<h2><a href="/jobspec/{{ jobspec.name }}">{{ jobspec.name }}</a> ({{ job_status['id'] }})</h2>

% if job_status['exit_code'] == 0:
    <span class="button green">Passed</span>
% else:
    <span class="button red">Failed`</span>
% end

<ul id="job-status-summary">
    <li><b>ID</b>: {{ job_status['id'] }}</li>
    <li><b>Status</b>: {{ job_status['status'] }}</li>
    <li><b>Exit-code</b>: {{ job_status['exit_code'] }}</li>
    <li><b>Started</b>: {{ time_start_str }}</li>
    <li><b>Ended</b>: {{ time_end_str }}</li>
    <li><b>Build time</b>: {{ duration.duration(job_status['time_end'] - job_status['time_start']) }}</li>
</ul>

<h3>Environment</h3>
<table id="job-status-env">
    % for k, v in job_status['env'].items():
        <tr>
            <td><b>{{ k }}</b></td>
            <td>{{ v }}</td>
        </tr>
    % end
</table>

<h3>Output</h3>
<pre>{{ job_status['output'] }}</pre>

</main>
