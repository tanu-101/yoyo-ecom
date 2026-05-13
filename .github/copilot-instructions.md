# GitHub Copilot Instructions

Read `AGENTS.md` first. It is the compact source of truth for AI coding agents.

Then use these only when relevant:

- `.agent/instructions/core.md`
- `.agent/instructions/backend.md`
- `.agent/instructions/api.md`
- `.agent/instructions/testing.md`
- `docs/api-v1-contract.md`
- `docs/database-final.md`
- `docs/backend-plan.md`

Core rule: keep Django views thin, put reads in selectors, writes/business rules in services,
and add pytest coverage for every behavior change.
