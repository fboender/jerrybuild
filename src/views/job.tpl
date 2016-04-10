% rebase('base.tpl', title='Job')
<main id="job-result">
<h2>{{ jobspec.name }} ({{ job_status['id'] }})</h2>

% if job_status['exit_code'] == 0:
    <span class="button green">Passed</span>
% else:
    <span class="button red">Failed`</span>
% end

<ul id="job-status-summary">
    <li><b>ID</b>: {{ job_status['id'] }}</li>
    <li><b>Status</b>: {{ job_status['status'] }}</li>
    <li><b>Exit-code</b>: {{ job_status['exit_code'] }}</li>
</ul>

<h3>Output</h3>
<pre>{{ job_status['output'] }}</pre>

</main>
