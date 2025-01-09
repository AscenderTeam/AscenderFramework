from ascender.core.database.engine import DatabaseEngine
from ascender.core.database.orms.sqlalchemy import SQLAlchemyORM
from ascender.core.di.abc.base_injector import Injector
from ascender.core.di.interface.provider import Provider
from ascender.core.repositories import IdentityRepository, Repository


def provideRepository(repo: type[Repository] | type[IdentityRepository]) -> Provider:
    """
    Repository provider, for supplying module with repository

    Args:
        repo (Repository | IdentityRepository): Repository to add
    """
    return {
        "provide": repo,
        "use_factory": lambda injector, engine: repository_factory(injector, engine, repo),
        "deps": [Injector, DatabaseEngine]
    }


def repository_factory(
    injector: Injector,
    database_engine: DatabaseEngine,
    repository: type[Repository | IdentityRepository]
):
    if isinstance(database_engine.engine, SQLAlchemyORM):
        repository = repository(database_engine.generate_context())
        repository._injector = injector
        return repository
    
    repository = repository()
    repository._injector = injector
    
    return repository
