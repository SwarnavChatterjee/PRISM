# Contributing to PRISM

## For the SIH Team

This document is for our 5-person team during the 5-day sprint.

### Workflow

1. **Pull latest before starting work:**
```bash
   git pull origin main
```

2. **Work on your assigned module** (see [Final Implementation Plan](docs/final-implementation-plan.md))

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
cat > .env.example << 'EOF'
# Database
DATABASE_URL=sqlite:///compliance.db

# Framework (default)
DEFAULT_FRAMEWORK=cis_benchmarks

# Claude API (for Tier 3 LLM fallback)
ANTHROPIC_API_KEY=sk-...  # Get from https://console.anthropic.com/

# Environment
ENVIRONMENT=development  # or production

# Logging
LOG_LEVEL=INFO
