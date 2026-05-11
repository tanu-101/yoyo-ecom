# Review Code Changes

Review the current changes or the specified files:

## Review Checklist

### Correctness
- [ ] Does the code do what it's supposed to do?
- [ ] Are there any obvious bugs?
- [ ] Are edge cases handled?
- [ ] Are errors handled properly?

### Security
- [ ] Any SQL injection vulnerabilities?
- [ ] Any XSS vulnerabilities?
- [ ] Sensitive data being logged?
- [ ] Proper authorization checks?

### Django Patterns
- [ ] Models inherit from base models (UUIDModel, TimeStampedModel)?
- [ ] Business logic in services (not views)?
- [ ] Query logic in selectors (not views)?
- [ ] Proper import ordering?

### Code Quality
- [ ] Following project conventions?
- [ ] Proper type hints?
- [ ] No code duplication?
- [ ] Clear variable/function names?

### Testing
- [ ] Tests for new functionality?
- [ ] Edge cases tested?
- [ ] Permissions tested?

## Suggestions
Provide specific, actionable feedback with code examples if needed.