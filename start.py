"""
## Ascender WebFramework

A simple and powerful web framework for python. Developed by [Ascender](https://ascender.space)
"""
from dotenv import load_dotenv
from core.application import Application
from bootstrap import Bootstrap

load_dotenv()
app = Application(on_server_start=Bootstrap.server_boot_up, on_server_runtime_error=getattr(Bootstrap, "server_runtime_error", None), on_cli_run=getattr(Bootstrap, "cli_boot_up", None))

if __name__ == '__main__':
    app.run_cli()