% import time, datetime
% if job_status is None:
    Never built
% elif not hasattr(job_status, 'time_start') or job_status.time_start is None:
    Unknown
% else:
    {{ time.strftime("%Y-%m-%d %H:%M:%S", datetime.datetime.fromtimestamp(job_status.time_start).timetuple()) }}
% end
