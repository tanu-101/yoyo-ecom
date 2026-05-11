# Claude Code Instructions - E-Commerce Management System

<links>
- Core Rules: [.agent/instructions/core.md](.agent/instructions/core.md)
- Backend Patterns: [.agent/instructions/backend.md](.agent/instructions/backend.md)
- API Specs: [.agent/instructions/api.md](.agent/instructions/api.md)
- Testing: [.agent/instructions/testing.md](.agent/instructions/testing.md)
</links>

<rules>
- Use XML tags for structure.
- Prioritize token efficiency.
- Follow the thin-view, fat-service architecture.
</rules>

<commands>
- Lint: `cd backend && ruff check .`
- Test: `cd backend && pytest`
- Type Check: `cd backend && mypy .`
</commands>
