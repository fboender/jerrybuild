% rebase('base.tpl', title='Projects')
% job_status_button = include('helpers/job_status.tpl')['job_status_button']
<main id="overview">
<ul id="job-status">
% for name in sorted(job_status.keys()):
    <li>
        <div class="job-name"><a href="/job/definition/{{ name }}">{{ name }}</a></div>
        <div class="job-latest">
            % if job_status[name] is not None:
                % job_status_button(job_status[name]['exit_code'], job_status[name]['id'])
            % else:
                <span class="button gray">Never run</span>
            % end
        <div>
    </li>
% end
</ul>
</main>
