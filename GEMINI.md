# Gemini CLI Instructions - E-Commerce Management System

<links>
- Core Rules: [.agent/instructions/core.md](.agent/instructions/core.md)
- Backend Patterns: [.agent/instructions/backend.md](.agent/instructions/backend.md)
- API Specs: [.agent/instructions/api.md](.agent/instructions/api.md)
- Testing: [.agent/instructions/testing.md](.agent/instructions/testing.md)
</links>

<context>
This project is a modular Django monolith. Follow the Service/Selector pattern strictly.
Always use UUIDModel and SoftDeleteModel for new models.
</context>

<workflows>
1. **Research**: Check existing models/services in `apps/`.
2. **Implement**: Start with Models -> Migrations -> Selectors -> Services -> Views.
3. **Verify**: Run `ruff check`, `mypy`, and `pytest`.
</workflows>
