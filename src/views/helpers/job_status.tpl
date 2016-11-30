%# Display a button that shows the status of the job.
%#id = {{ job_status.id }} <br>
%#exit_code = {{ job_status.exit_code }} <br>
%#status = {{ job_status.status }}
% if job_status is None:
    <span class="status-button gray"><i class="fa fa-question-circle" aria-hidden="true"></i> Never built</span>
% elif job_status.status == 'queued':
    <a href="/job/{{ job_status.id }}/status"><span class="status-button light-blue"><i class="fa fa-clock-o" aria-hidden="true"></i> Queued<span class="pulse">...</span></span></a>
% elif job_status.status == 'running':
    <a href="/job/{{ job_status.id }}/status"><span class="status-button blue"><i class="fa fa-clock-o" aria-hidden="true"></i> Building<span class="pulse">...</span></span></a>
% elif job_status.status == 'aborted':
    <a href="/job/{{ job_status.id }}/status"><span class="status-button red"><i class="fa fa-check" aria-hidden="true"></i> Aborted</span></a>
% elif job_status.status == 'done':
    % if job_status.exit_code == 0:
        <a href="/job/{{ job_status.id }}/status"><span class="status-button green"><i class="fa fa-check" aria-hidden="true"></i> Passed</span></a>
    % else:
        <a href="/job/{{ job_status.id }}/status"><span class="status-button red"><i class="fa fa-exclamation-circle" aria-hidden="true"></i> Failed</span></a>
    % end
% else:
    <a href="/job/{{ job_status.id }}/status"><span class="status-button red"><i class="fa fa-exclamation-circle" aria-hidden="true"></i> ???</span></a>
% end
