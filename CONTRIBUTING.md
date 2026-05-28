# Contributing to F1 Intelligence Hub

## Development Workflow

1. **Fork** the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit changes following [Conventional Commits](https://www.conventionalcommits.org/)
4. Push to your branch and open a Pull Request

## Development Setup

```bash
# Install with dev dependencies
make install-dev

# Or manually:
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install ruff mypy pytest pytest-cov pre-commit
pre-commit install
```

## Code Standards

### Python
- **Format**: Ruff (line length 120) — `make format`
- **Lint**: Ruff — `make lint`
- **Types**: mypy with `--ignore-missing-imports` — `make typecheck`
- **Tests**: pytest with coverage — `make test`
- Logging: use `logging.getLogger(__name__)` — no `print()` statements

### Commit Convention

```
<type>: <short description>

<body (optional)>
```

Types: `feat`, `fix`, `refactor`, `docs`, `style`, `chore`, `test`, `ci`

## PR Checklist

- [ ] `make lint` passes
- [ ] `make typecheck` passes
- [ ] `make test` passes (coverage >= 70%)
- [ ] No `print()` — use `logging` instead
- [ ] No secrets or credentials committed
- [ ] Documentation updated if needed

## CI Pipeline

Every push/PR triggers:
1. **Lint** — Ruff lint + format check
2. **Typecheck** — mypy static analysis
3. **Test** — pytest with coverage (min 70%)
4. **Docker** — image builds successfully
