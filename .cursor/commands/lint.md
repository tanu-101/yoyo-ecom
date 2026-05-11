# Check Code Quality

Run linting and formatting checks on the project.

## Commands

### Lint
```bash
cd backend && ruff check .
```

### Format
```bash
cd backend && ruff format .
```

### Type Check
```bash
cd backend && mypy .
```

## Common Issues

- `E501` - Line too long (max 100)
- `F401` - Unused imports
- `F841` - Unused variables
- `E302` - Expected 2 blank lines

## Fix All
```bash
cd backend && ruff check . --fix && ruff format .
```