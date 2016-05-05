% def job_status_button(exit_code, job_id=None):
    %# Display a button that shows the status of the job.
    % if exit_code is None:
        % if job_id is None:
            <span class="status-button blue"><i class="fa fa-clock-o" aria-hidden="true"></i> Building<span class="pulse">...</span></span>
        % else:
            <a href="/job/status/{{ job_id }}"><span class="status-button blue"><i class="fa fa-clock-o" aria-hidden="true"></i> Building<span class="pulse">...</span></span></a>
        % end
    % elif exit_code == 0:
        % if job_id is None:
            <span class="status-button green"><i class="fa fa-check" aria-hidden="true"></i> Passed</span>
        % else:
            <a href="/job/status/{{ job_id }}"><span class="status-button green"><i class="fa fa-check" aria-hidden="true"></i> Passed</span></a>
        
        % end
    % else:
        % if job_id is None:
            <span class="status-button red"><i class="fa fa-exclamation-circle" aria-hidden="true"></i> Failed</span>
        % else:
            <a href="/job/status/{{ job_id }}"><span class="status-button red"><i class="fa fa-exclamation-circle" aria-hidden="true"></i> Failed</span></a>
        % end
    % end
% end
