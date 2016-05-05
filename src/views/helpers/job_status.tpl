%# Display a button that shows the status of the job.
% if job_status is None:
    <span class="status-button gray"><i class="fa fa-question-circle" aria-hidden="true"></i> Never run</span>
% elif job_status['exit_code'] is None:
    % if job_status['id'] is None:
        <span class="status-button blue"><i class="fa fa-clock-o" aria-hidden="true"></i> Building<span class="pulse">...</span></span>
    % else:
        <a href="/job/status/{{ job_status['id'] }}"><span class="status-button blue"><i class="fa fa-clock-o" aria-hidden="true"></i> Building<span class="pulse">...</span></span></a>
    % end
% elif job_status['exit_code'] == 0:
    % if job_status['id'] is None:
        <span class="status-button green"><i class="fa fa-check" aria-hidden="true"></i> Passed</span>
    % else:
        <a href="/job/status/{{ job_status['id'] }}"><span class="status-button green"><i class="fa fa-check" aria-hidden="true"></i> Passed</span></a>
    
    % end
% else:
    % if job_status['id'] is None:
        <span class="status-button red"><i class="fa fa-exclamation-circle" aria-hidden="true"></i> Failed</span>
    % else:
        <a href="/job/status/{{ job_status['id'] }}"><span class="status-button red"><i class="fa fa-exclamation-circle" aria-hidden="true"></i> Failed</span></a>
    % end
% end
