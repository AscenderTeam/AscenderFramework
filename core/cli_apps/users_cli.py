from core.cli import GenericCLI
from core.cli.application import ContextApplication
from core.cli.async_module import CoroCLI
from core.cli.main import console_command
from core.extensions.authentication import AscenderAuthenticationFramework

class UsersCLI(GenericCLI):
    
    @console_command
    def test(self, ctx: ContextApplication, alive: bool, name: str):
        ctx.console_print(f"{name} is alive: {alive}")

    @console_command
    @CoroCLI(is_tortoise=True)
    async def create_user(self, ctx: ContextApplication, username: str, password: str):
        # Initialize authentication framework
        await ctx.application.use_database_cli()
        ctx.application.use_authentication()
        ctx.console_print("[cyan]Creating user, hold on...[/cyan] 🚀")
        # Create user
        await AscenderAuthenticationFramework.auth_provider.create_user(username, password)
        ctx.console_print("[bold green]User created successfully![/bold green]")
    
    @console_command
    @CoroCLI(is_tortoise=True)
    async def create_superuser(self, ctx: ContextApplication, username: str, password: str):
        # Initialize authentication framework
        await ctx.application.use_database_cli()
        ctx.application.use_authentication()
        ctx.console_print("[cyan]Creating superuser, hold on...[/cyan] 🚀")
        # Create user
        await AscenderAuthenticationFramework.auth_provider.create_superuser(username, password)
        ctx.console_print("[bold green]Superuser created successfully![/bold green]")