% rebase('base.tpl', title='Job')
% import datetime
% import time
% import tools
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
    time_duration = tools.duration(job_status['time_end'] - job_status['time_start'])
elif job_status['time_start'] is not None:
    time_duration = tools.duration(time.time() - job_status['time_start'])
end
%>
<main id="job-result">
<h2><a href="/jobspec/{{ jobspec.name }}">{{ jobspec.name }}</a> ({{ job_status['id'] }})</h2>

% job_status_button(job_status['exit_code'])

<table id="job-status-overview">
    <tr><th>ID</th><td>{{ job_status['id'] }}</td></tr>
    <tr><th>Status</th><td>{{ job_status['status'] }}</td></tr>
    <tr><th>Exit code</th><td>{{ job_status['exit_code'] }}</td></tr>
    <tr><th>Started</th><td>{{ time_start_str }}</td></tr>
    <tr><th>Ended</th><td>{{ time_end_str }}</td></tr>
    <tr><th>Build time</th><td>{{ time_duration }}</td></tr>
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
