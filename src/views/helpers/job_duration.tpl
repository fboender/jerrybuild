<%
import tools
time_duration = "Never built"

if job_status is not None and 'time_start' in job_status:
    if job_status['time_start'] is not None and job_status['time_end'] is not None:
        time_duration = tools.duration(job_status['time_end'] - job_status['time_start'])
    elif job_status['time_start'] is not None:
        time_duration = tools.duration(time.time() - job_status['time_start'])
    end
end
%>
{{ time_duration }}
