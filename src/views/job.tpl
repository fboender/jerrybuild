% rebase('base.tpl', title='Job')
% import datetime
% import time
% import duration
% job_status_button = include('helpers/job_status.tpl')['job_status_button']
<%
time_start_str = "Not started"
time_end_str = "Still running"
time_duration = "Unknown"

if job_status['time_start'] is not None:
    time_start_str = time.strftime("%Y-%m-%dT%H:%M:%S", datetime.datetime.fromtimestamp(job_status['time_start']).timetuple())
end
if job_status['time_end'] is not None:
    time_end_str = time.strftime("%Y-%m-%dT%H:%M:%S", datetime.datetime.fromtimestamp(job_status['time_end']).timetuple())
end

if job_status['time_start'] is not None and job_status['time_end'] is not None:
    time_duration = duration.duration(job_status['time_end'] - job_status['time_start'])
elif job_status['time_start'] is not None:
    time_duration = duration.duration(time.time() - job_status['time_start'])
end
%>
<main id="job-result">
<h2><a href="/jobspec/{{ jobspec.name }}">{{ jobspec.name }}</a> ({{ job_status['id'] }})</h2>

% job_status_button(job_status['exit_code'])

<ul id="job-status-summary">
    <li><b>ID</b>: {{ job_status['id'] }}</li>
    <li><b>Status</b>: {{ job_status['status'] }}</li>
    <li><b>Exit-code</b>: {{ job_status['exit_code'] }}</li>
    <li><b>Started</b>: {{ time_start_str }}</li>
    <li><b>Ended</b>: {{ time_end_str }}</li>
    <li><b>Build time</b>: {{ time_duration }}</li>
</ul>

<h3>Environment</h3>
<table id="job-status-env">
    % for k, v in sorted(job_status['env'].items()):
        <tr>
            <td><b>{{ k }}</b></td>
            <td>{{ v }}</td>
        </tr>
    % end
</table>

<h3>Output</h3>
<pre>{{ job_status['output'] }}</pre>

</main>
