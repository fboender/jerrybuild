% rebase('base.tpl', title='Projects')
<main id="overview">
<ul id="job-status">
% for name in sorted(job_status.keys()):
    <li>
        <div class="job-name">{{ name }}</div>
        <div class="job-latest">
            % if job_status[name] is not None:
                % if job_status[name]['exit_code'] == 0:
                    <a href="job/{{ job_status[name]['id'] }}"><span class="button green">Passed</span></a>
                % else:
                    <a href="job/{{ job_status[name]['id'] }}"><span class="button red">Failed`</span></a>
                % end
            % else:
                <span class="button gray">Never run</span>
            % end
        <div>
    </li>
% end
</ul>
</main>
