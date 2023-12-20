import os
from pathlib import Path
from typing import Any
from typing import Generator, Iterator

from langchain.chat_models import ChatOpenAI
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler

from clis.controller_cli.chains.controller_file_chain import ControllerFileGenerationChain
from clis.controller_cli.chains.md_out import MarkdownCodeblockParser
from clis.controller_cli.chains.name_chain import ControllerNameGenerationChain
from clis.controller_cli.constants import ControllerConstants


class ControllerCreator:
    def __init__(self, controller_name: str, controller_path: str = "controllers") -> None:
        self.controller_constants = ControllerConstants(controller_name, controller_path)
        self.controller_path = controller_path

    def generate_name(self, description: str) -> str:
        chain = ControllerNameGenerationChain.from_llm(llm=ChatOpenAI(model=os.environ['SLOW_MODEL_NAME']), verbose=False)
        new_name = chain.run(stop='\n', description=description)
        self.controller_constants = ControllerConstants(new_name, self.controller_path)
        return new_name

    def create_controller(self) -> Generator[str, None, None]:
        path_manager = Path(self.controller_constants.controllers_path,
                            self.controller_constants.controller_name.lower())

        if not path_manager.exists():
            path_manager.mkdir()

        # Handle files
        mandatory_files = self.controller_constants.get_mandatory_files()

        for mandatory_file in mandatory_files:
            self.create_file(mandatory_file["path"], mandatory_file["content"])
            yield mandatory_file['name']

    def generate_controller(self, description_prompt: str, controller_name: str) -> Generator[str, None, None]:
        path_manager = Path(self.controller_constants.controllers_path,
                            self.controller_constants.controller_name.lower())

        if not path_manager.exists():
            path_manager.mkdir()

        # Handle files
        mandatory_files = self.controller_constants.get_mandatory_files() +\
                          self.controller_constants.get_optional_files()
        new_formatted_files = []
        # print(mandatory_files)
        for mandatory_file in mandatory_files:
            chain = ControllerFileGenerationChain.from_llm(llm=ChatOpenAI(model=os.environ['SLOW_MODEL_NAME']), verbose=False)
            parser = MarkdownCodeblockParser()

            formatted_blank = """{path}:
                                ```current_state
                                {blank}
                                ```""".format(path=mandatory_file["path"], blank=mandatory_file["content"])
            file = chain.run(format_instructions=parser.get_format_instructions(),
                             formatted_blank=formatted_blank,
                             description=description_prompt,
                             controller_name=controller_name,
                             previous_files_created='\n'.join(new_formatted_files))
            output = parser.parse(file)

            new_formatted_files.append(formatted_blank)
            self.create_file(mandatory_file["path"], '\n'.join(output))
            yield mandatory_file['path'], '\n'.join(output)

    def create_optional_files(self) -> Generator[str, None, None]:
        path_manager = Path(self.controller_constants.controllers_path,
                            self.controller_constants.controller_name.lower())

        if not path_manager.exists():
            path_manager.mkdir()

        # Handle files
        optional_files = self.controller_constants.get_optional_files()

        for optional_file in optional_files:
            self.create_file(optional_file["path"], optional_file["content"])
            yield optional_file['name'], optional_file["content"]

    def create_file(self, fpath: str, contents: str):
        with open(fpath, "w") as f:
            f.write(contents)
