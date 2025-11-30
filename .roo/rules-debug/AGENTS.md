# AGENTS.md

This file provides guidance to agents when working with code in this repository.

### Debug Mode Specific Rules

## Critical Project Patterns

### Test Configuration Gotcha
- Tests require manual config file creation from template
- Config file path relative to tests/ directory (not project root)
- Multiple config sections needed: bot, message, app, webhook

### Error Handling Pattern
- API calls don't validate responses - raw requests.Response returned
- No automatic retry logic in base API class
- Subclasses handle their own error cases