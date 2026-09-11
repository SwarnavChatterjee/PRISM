# Contributing to PRISM

## For the SIH Team

This document covers the workflow for changes to the current PRISM codebase.

### Workflow

1. **Pull latest before starting work:**
```bash
   git pull origin main
```

2. **Work on the relevant module** (see [Architecture](docs/ARCHITECTURE.md) and the [README](README.md))

3. **Commit frequently** (at least once per day):
```bash
   git add .
   git commit -m "[Day X] [Module] Brief description of what was done"
```
   
   Examples:
   - `git commit -m "[Day 2] Normalization: Implement Tier 1 regex matching"`
   - `git commit -m "[Day 2] Frontend: Build upload screen"`
   - `git commit -m "[Day 3] Training: Save mappings to database"`

4. **Push at end of day:**
```bash
   git push origin main
```

5. **Never** force push or rewrite history (`git push --force`) — it makes it hard to track what everyone did.

### Commit Message Format

Use a short imperative message that names the affected area, for example:

```text
Frontend: improve finding filters
Engine: add Juniper pattern mapping
Tests: cover faulty Cisco demo config
```

Keep generated files, local databases, credentials, and dependency folders out of commits. The repository `.gitignore` is the source of truth for those exclusions.
