% import time, datetime, tools
% if job_status is None:
    Never built
% elif 'time_end' not in job_status:
    Unknown
% elif job_status['time_end'] is None:
    Still running
% else:
    <abbr title="{{ time.strftime("%Y-%m-%d %H:%M:%S", datetime.datetime.fromtimestamp(job_status['time_end']).timetuple()) }}">{{ tools.duration(time.time() - job_status['time_end']) }}</abbr> ago
    
% end
