from clis.controller_cli.cli_processor import ControllerCLI
from clis.migrate_cli import MigrateCLI
from core.application import Application
from core.cli.main import CLI


class Bootstrap:

    @staticmethod
    def server_boot_up(app: Application):
        app.use_database()
        app.loader_module.register_controller({
            'name': "Research API",
            'base_path': 'controllers',
            'exclude_controllers': [],
            'initialize_all_controllers': True,
        })

        # Load all controllers
        app.loader_module.load_all_controllers()
    
    @staticmethod
    def cli_boot_up(_: Application, cli: CLI):
        cli.register_generic_command(MigrateCLI())
        cli.register_generic_command(ControllerCLI())