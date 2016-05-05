% import time, datetime
% if 'time_start' not in job_status or job_status['time_start'] is None:
    Unknown
% else:
    {{ time.strftime("%Y-%m-%d %H:%M:%S", datetime.datetime.fromtimestamp(job_status['time_start']).timetuple()) }}
% end
