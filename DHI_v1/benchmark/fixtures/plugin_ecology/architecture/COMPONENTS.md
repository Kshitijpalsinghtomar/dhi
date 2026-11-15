# Northstar components

| Component | Responsibility | Depends on |
|---|---|---|
| Work item API | Stores work item status, priority, estimates and dependencies | PostgreSQL |
| Dependency exporter | Emits dependency graph CSV | Work item API |
| Weekly summary | Groups work items by due-date week | Work item API |
| Approval service | Requires two approvers for production configuration changes | Identity service |
| CSV exporter | Produces workload and acceptance-test exports | Work item API |

## Runtime constraints
- The weekly summary uses UTC timestamps as source values.
- The dependency exporter is read-only.
- The approval service must reject a production change with fewer than two distinct approvals.
- No deployment or production mutation is permitted in this benchmark fixture.
