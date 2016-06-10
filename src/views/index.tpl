<%
reload_page = False
for job_status in job_statusses.values():
    if job_status is not None and job_status['status'] not in ('done', 'internal_error'):
        reload_page = True
    end
end
%>
% rebase('base.tpl', title='Projects', reload_page=reload_page)
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
                % include('helpers/job_time_end_ago.tpl')
            </td>
            <td>
                % include('helpers/job_duration.tpl')
            </td>
        </tr>
    % end
</table>

</main>
