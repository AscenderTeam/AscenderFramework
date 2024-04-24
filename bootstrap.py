from core.application import Application
from core.cli.processor import CLI


class Bootstrap:

    @staticmethod
    def server_boot_up(app: Application):
        app.use_database()
        app.use_authentication()
        app.loader_module.register_controller({
            'name': "API Service",
            'base_path': 'controllers',
            'exclude_controllers': [],
            'initialize_all_controllers': True,
        })
        # Load all controllers
        app.loader_module.load_all_controllers()
    
    @staticmethod
    def cli_boot_up(_: Application, cli: CLI):
        pass