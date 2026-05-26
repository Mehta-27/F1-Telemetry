# Contributing

## Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit changes following conventional commits
4. Push to your branch
5. Open a Pull Request

## Code Standards

### Python
- Format with `ruff` (line length 120)
- Type hints on all function signatures
- Docstrings for public modules, classes, and functions

### TypeScript / React
- Strict TypeScript mode enforced
- Use the existing component patterns (glass-panel, carbon-surface)
- No inline styles — use CSS variables from `globals.css`

## Commit Convention

```
<type>: <short description>

<optional body>
```

Types: `feat`, `fix`, `refactor`, `docs`, `style`, `chore`

## PR Checklist

- [ ] Backend: `python -m api` starts without errors
- [ ] Frontend: `npm run build` succeeds
- [ ] TypeScript: no `any` types leaking
- [ ] No secrets or credentials committed
