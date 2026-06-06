# Contributing to OncAI

## Development Workflow

```bash
# 1. Fork the repo
# 2. Create a feature branch
git checkout -b feature/amazing-feature

# 3. Make changes
# 4. Run tests
cd backend && pytest tests/ -v
cd ../frontend && npm run type-check && npm run build

# 5. Commit using Conventional Commits
git commit -m "feat(api): add SHAP force plot endpoint"

# 6. Push and open a PR
git push origin feature/amazing-feature
```

## Commit Message Format

```
<type>(<scope>): <description>

Types: feat | fix | docs | style | refactor | test | chore
Scope: api | model | frontend | ci | docker | docs
```

## Code Standards

**Python**: Black + isort + flake8
```bash
pip install black isort flake8
black backend/
isort backend/
flake8 backend/ --max-line-length=100
```

**TypeScript**: ESLint + Prettier
```bash
cd frontend
npm run lint
```

## Pull Request Checklist

- [ ] Tests pass (`pytest` + TypeScript build)
- [ ] No new linting errors
- [ ] README updated if behaviour changed
- [ ] Docstrings on new public functions
- [ ] No hardcoded secrets or file paths
