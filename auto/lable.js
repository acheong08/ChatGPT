const issue = context.payload.issue

const labelsToAdd = []
const labelConditions = [
  {label: 'bug', keywords: ['Bug', 'bug']},
  {label: 'enhancement', keywords: ['suggestion', 'enhancement', 'feature request', 'Feature request', 'Feature Request']},
  {label: 'documentation', keywords: ['docs', 'documentation', 'Wiki', 'wiki']},
  {label: 'help wanted', keywords: ['help wanted']},
  {label: 'question', keywords: ['question', 'Why', 'why', 'How', 'how']},
  {label: 'V1', keywords: ['V1', 'v1']},
  {label: 'V3', keywords: ['V3', 'v3']},
  {label: 'authentication', keywords: ['auth', 'Auth', 'token', 'Token', 'TOKEN', 'config', 'Config', 'CONFIG', 'Unauthorized', '401', '403', '502', '503', 'forbidden', 'Forbidden', 'access', 'block']},
  {label: 'network', keywords: ['openai.com', 'ssl', 'SSL', 'HTTPS', 'Connection', 'connection', 'proxy', 'Proxy', 'PROXY', 'VPN']},
  {label: 'CLI', keywords: ['command program', 'Command Program', 'CLI']}
]
// Add tags based on conditions
for (const {label, keywords} of labelConditions) {
    for (const keyword of keywords) {
        if (issue.title.includes(keyword)) {
            labelsToAdd.push(label)
            break
        }
    }
}
if (labelsToAdd.length == 0) {
    labelsToAdd.push('triage-needed')
}

console.log("All of tags:", labelsToAdd)

// Add tags
github.rest.issues.addLabels({
  owner: context.repo.owner,
  repo: context.repo.repo,
  issue_number: issue.number,
  labels: labelsToAdd
})