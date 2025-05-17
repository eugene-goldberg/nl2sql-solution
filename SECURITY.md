# Security Policy

## Sensitive Information

This repository contains code for translating natural language to SQL queries. To maintain security:

### Never Commit:
- API keys or tokens
- Database passwords
- Connection strings with credentials
- Any `.env` files
- Personal or proprietary data

### Always Use:
- Environment variables for sensitive configuration
- `.env.example` as a template
- Read-only database permissions where possible
- Input sanitization for user queries

## Reporting Security Issues

If you discover a security vulnerability, please:
1. Do NOT create a public issue
2. Email the maintainers privately
3. Include steps to reproduce the issue
4. Allow time for a fix before public disclosure

## Best Practices

1. **Database Access**: Always use least-privilege principles
2. **API Keys**: Rotate regularly and limit scope
3. **Queries**: Validate and sanitize all inputs
4. **Logging**: Never log sensitive information
5. **Dependencies**: Keep all packages updated