# Poetry Setup Guide for Co-Optimal

This guide will help you set up Poetry for the Co-Optimal project on any operating system.

## Quick Poetry Setup

### Step 1: Install Poetry

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -


#### Verify Installation
```bash
poetry --version
```

### Step 2: Project Setup

```bash
# Navigate to project directory
cd co-optimal

# Set Python version (if you have multiple Python versions)
poetry env use 3.12

# Install all dependencies
poetry install
```

### Step 3: Activate Virtual Environment

#### Method 1: Poetry's New Activate Command (Poetry 2.0+)
```bash
poetry env activate
```

#### Method 2: Manual Activation (if Method 1 doesn't work)
```bash
# Find the virtual environment path
poetry env info --path

# Activate manually (replace with your actual path)
# Windows PowerShell:
& "C:\Users\YourUsername\AppData\Local\pypoetry\Cache\virtualenvs\co-optimal-xxxxx-py3.12\Scripts\activate.ps1"

# macOS/Linux:
source /Users/YourUsername/Library/Caches/pypoetry/virtualenvs/co-optimal-xxxxx-py3.12/bin/activate
```


## 🎯 Best Practices

1. **Always use `poetry.lock`**: Commit this file to version control
2. **Use version constraints**: Specify version ranges in `pyproject.toml`
3. **Group dependencies**: Use dev dependencies for development tools
4. **Use `poetry run`**: For one-off commands instead of activation
5. **Keep dependencies updated**: Regularly run `poetry update`

## 🔗 Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry GitHub Repository](https://github.com/python-poetry/poetry)
- [Python Packaging User Guide](https://packaging.python.org/) 