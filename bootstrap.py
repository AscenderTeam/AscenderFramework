from controllers.auth.repository import AuthRepo
from core.application import Application
from core.cli.processor import CLI
from core.database.engine import DatabaseEngine
from core.database.types.orm_enum import ORMEnum
from core.identity.security import Security
from settings import DATABASE_CONNECTION, TORTOISE_ORM


class Bootstrap:

    @staticmethod
    def server_boot_up(app: Application):
        app.setup_docs(enabled=False)
        app.use_database(lambda e: Bootstrap.database_registry(app, e),
                         ORMEnum.SQLALCHEMY, DATABASE_CONNECTION)
        # app.use_authentication()
        app.loader_module.register_controller({
            'name': "API Service",
            'base_path': 'controllers',
            'exclude_controllers': [],
            'initialize_all_controllers': True,
        })
        # Load all controllers
        app.loader_module.load_all_controllers()
    
    @staticmethod
    def authorization_registry(security: Security):
        security.add_policy("isUser", lambda p: p.require_role("user"))

    @staticmethod
    def database_registry(app: Application, engine: DatabaseEngine):
        engine.load_entity("entities.user")
        engine.run_database()
        app.add_authorization(Bootstrap.authorization_registry,
                              identity_repository=engine.identity_repo(AuthRepo), 
                              auth_scheme="oauth2",
                              secret="asdwq231")

    @staticmethod
    def cli_boot_up(app: Application, cli: CLI):
        pass

    @staticmethod
    def plugin_boot_up(app: Application):
        pass