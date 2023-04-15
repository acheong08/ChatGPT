const assignees = ['acheong08'];
const assignee = assignees[Math.floor(Math.random() * assignees.length)];

console.log(`The question will assign to ${assignee}`)

// Add assignees
github.rest.issues.addAssignees({
    issue_number: context.issue.number,
    owner: context.repo.owner,
    repo: context.repo.repo,
    assignees: [assignee]
})

// Add comment
github.rest.issues.createComment({
    issue_number: context.issue.number,
    owner: context.repo.owner,
    repo: context.repo.repo,
    body: `👋 Thanks for reporting! your question will solve by ${assignee}`
})