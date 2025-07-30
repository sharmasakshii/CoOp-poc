# Alembic Database Migrations Guide

This document provides comprehensive guidance on using Alembic for database migrations in the Co-Optimal project.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Setup](#project-setup)
- [Database Models](#database-models)
- [Migration Commands](#migration-commands)
- [Migration Workflow](#migration-workflow)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## 🎯 Overview

Alembic is SQLAlchemy's database migration tool that allows you to:

- **Version Control Database Schema**: Track changes to your database structure
- **Automatic Migration Generation**: Generate migrations from model changes
- **Rollback Support**: Safely revert database changes
- **Environment Management**: Handle different database environments
- **Team Collaboration**: Share schema changes across development teams

### Why Alembic?

- **Production Ready**: Battle-tested in production environments
- **SQLAlchemy Integration**: Seamless integration with SQLAlchemy models
- **Flexible**: Supports complex migration scenarios
- **Reversible**: All migrations can be undone
- **Environment Aware**: Different configurations for development/production

## 🏗️ Project Setup

### Directory Structure
```
co-optimal/
├── alembic/                    # Alembic configuration directory
│   ├── versions/               # Migration files
│   │   └── 2025_07_26_2121-8f8ecb998390_initial_migration_create_users_table.py
│   ├── env.py                  # Environment configuration
│   ├── README                  # Alembic README
│   └── script.py.mako         # Migration template
├── alembic.ini                 # Alembic configuration file
├── co_optimal/
│   └── models/                 # SQLAlchemy models
│       ├── __init__.py
│       ├── base.py
│       └── user.py
└── Makefile                    # Migration shortcuts
```

### Configuration Files

#### `alembic.ini`
Main configuration file with:
- **File Template**: Timestamped migration files
- **Script Location**: Points to `alembic/` directory
- **Database URL**: Commented out (configured in `env.py`)

#### `alembic/env.py`
Environment configuration that:
- Imports your models for autogenerate support
- Configures database connection from environment variables
- Sets up both online and offline migration modes

## 🗃️ Database Models

### Base Model
```python
# co_optimal/models/base.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

### User Model Example
```python
# co_optimal/models/user.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    bio = Column(Text, nullable=True)
```

### Model Registration
```python
# co_optimal/models/__init__.py
from .base import Base
from .user import User

__all__ = ["Base", "User"]
```

## 🚀 Migration Commands

### Quick Reference (Makefile)
```bash
# Generate new migration from model changes
make migrate-generate

# Apply all pending migrations
make migrate-up

# Rollback last migration
make migrate-down

# Show migration history
make migrate-history

# Show current migration
make migrate-current

# Initialize database (first time)
make migrate-init
```

### Direct Poetry Commands
```bash
# Generate migration with custom message
poetry run alembic revision --autogenerate -m "Add user roles table"

# Apply migrations
poetry run alembic upgrade head

# Rollback migrations
poetry run alembic downgrade -1          # Rollback 1 migration
poetry run alembic downgrade base        # Rollback all migrations
poetry run alembic downgrade <revision>  # Rollback to specific revision

# Migration info
poetry run alembic current               # Current revision
poetry run alembic history               # All revisions
poetry run alembic show <revision>       # Show specific revision
```

## 🔄 Migration Workflow

### 1. Development Workflow

#### Step 1: Modify Models
```python
# Add new field to User model
class User(Base):
    # ... existing fields ...
    phone_number = Column(String(20), nullable=True)  # New field
```

#### Step 2: Generate Migration
```bash
make migrate-generate
# or
poetry run alembic revision --autogenerate -m "Add phone number to users"
```

#### Step 3: Review Generated Migration
```python
# Check the generated file in alembic/versions/
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'phone_number')
    # ### end Alembic commands ###
```

#### Step 4: Apply Migration
```bash
make migrate-up
# or
poetry run alembic upgrade head
```

### 2. Production Workflow

#### Pre-Deployment
```bash
# Test migration on staging
poetry run alembic upgrade head

# Check current state
poetry run alembic current

# Review pending migrations
poetry run alembic history
```

#### Deployment
```bash
# Apply migrations in production
poetry run alembic upgrade head

# Verify migration
poetry run alembic current
```

#### Rollback (if needed)
```bash
# Rollback to previous version
poetry run alembic downgrade -1

# Rollback to specific version
poetry run alembic downgrade <revision_id>
```

## 🛠️ Advanced Usage

### Manual Migrations

Sometimes you need manual migrations for complex changes:

```bash
# Create empty migration
poetry run alembic revision -m "Custom data migration"
```

```python
# Edit the generated file
def upgrade() -> None:
    # Custom SQL or Python code
    connection = op.get_bind()
    connection.execute(text("""
        UPDATE users 
        SET full_name = CONCAT(first_name, ' ', last_name) 
        WHERE full_name IS NULL
    """))

def downgrade() -> None:
    # Reverse the changes
    pass
```

### Data Migrations

For migrating data along with schema:

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

def upgrade() -> None:
    # Schema change
    op.add_column('users', sa.Column('status', sa.String(20), nullable=True))
    
    # Data migration
    users_table = table('users',
        column('id', sa.Integer),
        column('is_active', sa.Boolean),
        column('status', sa.String)
    )
    
    # Update existing data
    op.execute(
        users_table.update()
        .where(users_table.c.is_active == True)
        .values(status='active')
    )
    
    op.execute(
        users_table.update()
        .where(users_table.c.is_active == False)
        .values(status='inactive')
    )
```

### Branch Management

For handling multiple feature branches:

```bash
# Create branch-specific migration
poetry run alembic revision -m "Feature branch migration" --branch-label feature_branch

# Merge branches
poetry run alembic merge -m "Merge feature branch" head1 head2
```

## 🎯 Best Practices

### 1. Migration Naming
```bash
# Good migration names
poetry run alembic revision --autogenerate -m "Add user authentication tables"
poetry run alembic revision --autogenerate -m "Remove deprecated email_verified column"
poetry run alembic revision --autogenerate -m "Create indexes for user search"

# Avoid generic names
poetry run alembic revision --autogenerate -m "Update"  # ❌
poetry run alembic revision --autogenerate -m "Fix"     # ❌
```

### 2. Review Generated Migrations
Always review auto-generated migrations:

```python
# Check for potential issues
def upgrade() -> None:
    # ⚠️ Review: Will this drop data?
    op.drop_column('users', 'old_field')
    
    # ✅ Better: Migrate data first
    # 1. Add new column
    # 2. Migrate data
    # 3. Drop old column (in separate migration)
```

### 3. Backwards Compatibility
Ensure migrations are reversible:

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('new_field', sa.String(50)))

def downgrade() -> None:
    # Always implement downgrade
    op.drop_column('users', 'new_field')
```

### 4. Testing Migrations
```bash
# Test migration up and down
poetry run alembic upgrade head
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

### 5. Large Table Migrations
For large tables, consider:

```python
# Add column with default
op.add_column('users', sa.Column('new_field', sa.String(50), server_default='default_value'))

# Remove default in separate migration
op.alter_column('users', 'new_field', server_default=None)
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
**Error**: `ModuleNotFoundError: No module named 'co_optimal'`

**Solution**: Check `alembic/env.py` path configuration:
```python
# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
```

#### 2. Database Connection Issues
**Error**: `could not connect to server: Connection refused`

**Solutions**:
```bash
# Check database is running
docker ps | grep postgres

# Check environment variables
cat co_optimal/.env

# Test connection manually
docker exec -it co-optimal-postgres psql -U postgres -d co_optimal
```

#### 3. Migration Conflicts
**Error**: `Multiple head revisions are present`

**Solution**:
```bash
# Show heads
poetry run alembic heads

# Merge heads
poetry run alembic merge -m "Merge conflicting migrations" head1 head2
```

#### 4. Model Changes Not Detected
**Issue**: Autogenerate doesn't detect model changes

**Solutions**:
```python
# Check model is imported in __init__.py
from .user import User  # Must be imported

# Check model inherits from Base
class User(Base):  # Must inherit from Base
    pass
```

### Diagnostic Commands
```bash
# Check current state
poetry run alembic current -v

# Show migration history
poetry run alembic history -v

# Check for issues
poetry run alembic check

# Show SQL without executing
poetry run alembic upgrade head --sql
```

## 📚 Examples

### Complete Migration Example

#### 1. Add New Model
```python
# co_optimal/models/role.py
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 2. Update Models Init
```python
# co_optimal/models/__init__.py
from .base import Base
from .user import User
from .role import Role  # Add new import

__all__ = ["Base", "User", "Role"]
```

#### 3. Generate Migration
```bash
poetry run alembic revision --autogenerate -m "Add roles table"
```

#### 4. Review and Apply
```bash
# Review the generated file
cat alembic/versions/*_add_roles_table.py

# Apply migration
poetry run alembic upgrade head

# Verify
poetry run alembic current
```

### Data Migration Example
```python
"""Migrate user status from boolean to enum

Revision ID: abc123
Revises: def456
Create Date: 2025-01-01 12:00:00
"""

def upgrade() -> None:
    # Step 1: Add new column
    op.add_column('users', sa.Column('status', sa.String(20)))
    
    # Step 2: Migrate data
    connection = op.get_bind()
    connection.execute(text("""
        UPDATE users SET status = 'active' WHERE is_active = true;
        UPDATE users SET status = 'inactive' WHERE is_active = false;
    """))
    
    # Step 3: Make column non-nullable
    op.alter_column('users', 'status', nullable=False)

def downgrade() -> None:
    # Reverse the changes
    op.drop_column('users', 'status')
```

## 🔗 Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Migration Best Practices](https://alembic.sqlalchemy.org/en/latest/cookbook.html)
- [Database Migration Patterns](https://martinfowler.com/articles/evodb.html)

---

## 📞 Quick Help

For common tasks:

```bash
# Initialize database (first time)
make migrate-init

# Daily development
make migrate-generate  # After model changes
make migrate-up        # Apply changes

# Check status
make migrate-current   # Current revision
make migrate-history   # All revisions

# Emergency rollback
make migrate-down      # Rollback last migration
```

**Happy migrating! 🚀** 