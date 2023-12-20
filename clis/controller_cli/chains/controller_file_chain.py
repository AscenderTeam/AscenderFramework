from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel


class ControllerFileGenerationChain(LLMChain):
    """Chain to make a file based on the description"""

    @classmethod
    def from_llm(cls, llm: BaseLanguageModel, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        file_prompt = """
        The Ascender Framework Helper technical documentation:

In this file, we provided all necessery information about technical side of Framework, including releases notes!

Ascender Framework functionality & necessery infos:
- Framework was based on FastAPI and inspired by NestJS & Some parts of Laravel
- Framework has CLI support which makes it powerful tool, it also provides developers to make their own CLI
- Framework has Caching system, it uses file .asc_cache in root directory of project and supports 2 formats: 'TEXT' and 'JSON'
- All entrypoint commands are headed to start.py
- Currently framework has built-in asynchronous support for database using Tortoise ORM however other ORMS aren't supported yet

## Bootstrap and how it works
By default, when user installs framework. It's `bootstrap.py` is already setted up for user.
Here is how it looks like:
```py
from clis.controller_cli.cli_processor import ControllerCLI
from clis.migrate_cli import MigrateCLI
from core.application import Application
from core.cli.main import CLI


{bootstrap}
```
Currently bootstrap has 1 mandatory staticmethod method named `server_boot_up`. It must be there!
what about `cli_boot_up`, it's highly recommend to not remove it also, as you see: By default when you install framework, you'll have 2 methods inside `bootstrap.py`. However there is 3 of them
If user will remove `cli_boot_up` then some of additional but built-in CLIs won't be available to user

Here is outline of all methods of Bootstrap (required and not required):
1. server_boot_up (required) (app: Application) - This is required method for Bootstrap, it'll be called when server boots up and starts successfully, after executing `python3 start.py serve` in command shell
2. cli_boot_up (highly recommend to add) (app: Application, cli: CLI) - file start.py is entrypoint for executing CLI commands. If user will execute any type of CLI command, this method will be called. User can add his own custom logic or even register his own CLI command which is good practice
3. server_runtime_error (ex: Exception) - If it was set in Bootstrap. Then user can handle and catch any errors that occurs during server boot up or runtime.

## Controllers & How to create them
Controllers are main stuff in this framework. They are base of MVC architecture and however file that contains controller was named `endpoints.py`. Controller itself is `endpoints.py`

Let's breakdown each Mandatory and Optional files of controller:

1. endpoints.py - It's the file that contains endpoints well structured and which contains setup function that unites logic of service, repositories and database entities to one controller and initializates it
Certainly, endpoints.py is required to have 2 main things: Controller Class and setup() function, here is how they look like
```py
# Import @Controller and @Get decorators from core.utils
from core.utils.controller import Controller, Get

@Controller()
class Test:
    def __init__(self, test_service: TestService):
        self.test_service = test_service
    
    # Same as in FastAPI, but decorator is imported from core.utils.controller
    @Get()
    async def hello_endpoint(self):
        return self.test_service.get_hello()
```
This is an example of controller class, name of controller is `Test` just for example.
__init__ of controller has test_service. This is service to handle business logic, it is inside `service.py`. The instance of service is defined in setup() function

Here is an example of setup() function:
```py
# controllers/test/endpoints.py
from core.types import ControllerModule
from controllers.test.service import TestService
...

{setup_text}
```
As you see, we have 3 classes that are required in setup() and we have 3 mandatory files! So, Test class is controller class and goes to `endpoints.py`, TestService class goes to `service.py` and TestRepo class goes to `repository.py`

Alright! Let's head over to `service.py`
```
# controllers/test/service.py
from core.extensions.services import Service

class TestService(Service):
    def __init__(repository: TestRepo): # As like as was given bit upper
        self.repository = repository # You can define self.[how you want!]
    
    async def get_hello(self):
        # return await self.repository.my_fetching_function() - this is example, but we didn't passed entities so repository is useless now
        return "Hello world"
```
Easy you see? Nothing very complex. However we have some advantages:
1. def __mounted__(self): -> ... - This method will be called in initialization. As __init__ will be called when class of service is initailized but other service may not, then __mounted__ is callen when all controllers and their services were initialized. Also you can inject controller
2. self.inject_controller("ControllerName") -> None: ... - Injects controller, it has second parameter also, it is string (controller_name: str, parameter_name: Optional[str] = None) if we set parameter_name by custom then we can access it just writing self.parameter_name
3. After injecting controller:
```py
self.inject_controller("ControllerName")
print(self.controller_name) # Prints object of other controller
```
Highly recommended to use inject_controller inside __mounted__. And it can raise error if user will inject_controller inside __init__ because of controller initialization competition

Same done with repo:
```
# controllers/test/repository.py
from core.extensions.repository import Repository
# Import entity as annotation, for datatype hints... But don't use it directly inside methods

class TestRepo(Repository):
    def __init__(): # Here we have to receive data passed in setup()["repository_entities"]
        # self.entity_name = passed data
    
    # Here use code to fetch data
```
        Please help me with my python controller called `{controller_name}`:
        ===previous files for context
        {previous_files_created}
        ===
        
        I need now you to modify the single codeblock below to achieve this:
        {description}
        
        ===you are modifying this file:
        {formatted_blank}
        ===
        
        %OUTPUT_FORMAT
        {format_instructions}
        """
        prompt = PromptTemplate(
            template=file_prompt,
            input_variables=[
                "format_instructions",
                "controller_name",
                "description_prompt",
                "previous_files_created",
                "path",
            ],
            partial_variables={'setup_text':
                               '''def setup() -> ControllerModule:
    return {
        "controller": Test,
        "services": {
            "test": TestService, # This will be passed as `test`_service: TestService in __init__() of controller class
        },
        "repository": TestRepo, # This will be passed as repository: TestRepo in __init__() of TestService service class
        "repository_entities": {
            # "name_of_entity": (entity instance) - Will be passed as `name_of_entity`: (entity instance) as __init__() of TestRepo class
        }
    }''',
                               'bootstrap':"""class Bootstrap:

    @staticmethod
    def server_boot_up(app: Application):
        app.use_database()
        app.loader_module.register_controller({
            'name': "Ascender Framework API",
            'base_path': 'controllers',
            'exclude_controllers': [],
            'initialize_all_controllers': True,
        })

        # Load all controllers
        app.loader_module.load_all_controllers()
    
    @staticmethod
    def cli_boot_up(app: Application, cli: CLI):
        cli.register_generic_command(MigrateCLI())
        cli.register_generic_command(ControllerCLI())"""}
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)
