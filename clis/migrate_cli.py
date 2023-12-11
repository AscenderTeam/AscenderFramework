from typing import Optional
from core.cli.application import ContextApplication, Table, Panel
from core.cli.async_module import CoroCLI
from core.cli.main import GenericCLI, console_command
from aerich import Command
from core.utils.cacher import AscCacher
from settings import BASE_PATH, TORTOISE_ORM

class MigrateCLI(GenericCLI):
    app_name: str = "migrate"
    help: Optional[str] = "Migrate data from one database to another"
    
    def __init__(self):
        super().__init__()
        self._name = 'migrate'
        self._description = 'Migrate data from one database to another'
        self._author = 'Zahcoder34'
        self._version = '0.0.1'
        
        self.__cacher = AscCacher()
    
    # @console_command
    # def test(self, ctx: ContextApplication, helo: str):
    #     ctx.console_print('Hello world ' + helo)

    @console_command
    @CoroCLI(is_tortoise=True)
    async def migration_init(self, ctx: ContextApplication, app: str = 'models'):
        ctx.console_print('[info]Initializing migration database...[/info]')
        
        command = Command(TORTOISE_ORM, app=app, location=f'{BASE_PATH}/migrations')
        # Cache data
        self.__cacher.save_json_cache({"app": app, "location": f'{BASE_PATH}/migrations'}, "migrate_config", is_binary=True)

        await command.init()
        ctx.console_print('Creating migration database...')
        await command.init_db(safe=True)
        ctx.console_print('[bold green]Migration database created successfully[/bold green]')
        return
    
    @console_command
    @CoroCLI(is_tortoise=True)
    async def migration_migrate(self, ctx: ContextApplication, name: str = "update"):
        ctx.console_print('[info]Migrating database...[/info]')
        
        # Load cache data
        command_data = self.__cacher.load_json_cache("migrate_config", is_binary=True)

        if not command_data:
            ctx.console_print('[error]No migration database found[/error]')
            ctx.console_print('[info]Please run [underline]migrate init[/underline] before running this command[/info]')
            return
        
        command = Command(TORTOISE_ORM, **command_data)
        await command.init()

        migration_name = await command.migrate(name=name)
        ctx.console_print(f'[info]Migration created, {migration_name}...[/info]')
        ctx.console_print('[info]Updating database...[/info]')
        
        upgrade = await command.upgrade(True)
        
        ctx.console_print('[bold green]Database has been updated successfully![/bold green]')
        
        updated_data = Table(migration_name, title="Updated data")
        if not len(upgrade):
            return
        
        for item in upgrade:
            updated_data.add_row(item)

        ctx.console_print(table=updated_data)
        return

    @console_command
    @CoroCLI()
    async def migration_history(self, ctx: ContextApplication):
        command_data = self.__cacher.load_json_cache("migrate_config", is_binary=True)
        
        if not command_data:
            ctx.console_print('[error]No migration database found[/error]')
            ctx.console_print('[info]Please run [underline]migration init[/underline] before running this command[/info]')
            return
        
        command = Command(TORTOISE_ORM, **command_data)
        await command.init()
        history = await command.history()

        view = Panel("\n".join(history), title="Migration history", border_style="green")
        ctx.console_print(panel=view)
        
        await ctx.console_pause_async()