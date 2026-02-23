# sync-python-matrix

A pre-commit hook to sync Python versions in GitHub Actions workflow files with the classifiers in `pyproject.toml`.

```toml
classifiers = [
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
]
```

↓

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version:
          - 3.13
          - 3.14
```

## Usage

Add this to your .pre-commit-config.yaml

```yaml
- repo: https://github.com/34j/sync-python-matrix
rev: ''  # Use the sha / tag you want to point at
hooks:
    - id: sync-python-matrix
```
