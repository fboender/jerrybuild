% import time, datetime
% if job_status is None:
    Never built
% elif 'time_end' not in job_status:
    Unknown
% elif job_status['time_end'] is None:
    Still running
% else:
    {{ time.strftime("%Y-%m-%d %H:%M:%S", datetime.datetime.fromtimestamp(job_status['time_end']).timetuple()) }}
% end