% def job_status_button(exit_code, job_id=None):
    %# Display a button that shows the status of the job.
    % if exit_code is None:
        % if job_id is None:
            <span class="button blue">Building<span class="pulse">...</span></span>
        % else:
            <a href="/job/{{ job_id }}"><span class="button blue">Building<span class="pulse">...</span></span></a>
        % end
    % elif exit_code == 0:
        % if job_id is None:
            <span class="button green">Passed</span>
        % else:
            <a href="/job/{{ job_id }}"><span class="button green">Passed</span></a>
        % end
    % else:
        <span class="button red">Failed</span>
    % end
% end
