% import time, datetime
% if 'time_end' not in job_status:
    Unknown
% elif job_status['time_end'] is None:
    Still running
% else:
    {{ time.strftime("%Y-%m-%d %H:%M:%S", datetime.datetime.fromtimestamp(job_status['time_end']).timetuple()) }}
% end
