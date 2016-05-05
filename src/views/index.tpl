% rebase('base.tpl', title='Projects')
<main id="overview">
<table id="job-status">
    <tr>
        <th>&nbsp;</th>
        <th>Status</th>
        <th>Last build</th>
        <th>Last duration</th>
    </tr>
    % for name in sorted(job_statusses.keys()):
        % job_status = job_statusses[name]
        <tr>
            <td>
                <a href="/job/definition/{{ name }}">{{ name }}</a>
            </td>
            <td>
                % include('helpers/job_status.tpl')
            </td>
            <td>
                % include('helpers/job_time_end.tpl')
            </td>
            <td>
                % include('helpers/job_duration.tpl')
            </td>
        </tr>
    % end
</table>

</main>
