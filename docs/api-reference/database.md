# Database API

The Database API provides utilities for database connections, ORM integration, and repository patterns.

## Core Components

::: ascender.core.database.DatabaseEngine
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - generate_context


## Types & Objects

::: ascender.core.database.AppDBContext

::: ascender.core.database.ORMEnum
    options:
      show_root_heading: true
      show_source: true


::: ascender.core.database.provideDatabase
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## See Also

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/) - Official SQLAlchemy docs
- [Alembic Documentation](https://alembic.sqlalchemy.org/) - Database migrations
- [Repository Pattern](../database/repositories.md) - Repository pattern guide
