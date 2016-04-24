% rebase('base.tpl', title='Projects')
% import time
% import tools
% job_status_button = include('helpers/job_status.tpl')['job_status_button']
<main id="overview">
<table id="job-status">
    <tr>
        <th>&nbsp;</th>
        <th>Status</th>
        <th>Last build</th>
    </tr>
    % for name in sorted(job_status.keys()):
        <tr>
            <td><a href="/job/definition/{{ name }}">{{ name }}</a></td>
            <td>
                % if job_status[name] is not None:
                    % job_status_button(job_status[name]['exit_code'], job_status[name]['id'])
                % else:
                    <span class="button gray">Never run</span>
                % end
            </td>
            <td>
                % if job_status[name] is not None:
                    <p>{{ tools.duration(time.time() - job_status[name]['time_end']) }} ago </p>
                % end
            </td>
        </tr>
    % end
</table>

</main>
