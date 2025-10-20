import os
from ascender.clis.builder.build_service import BuildService
from ascender.core.cli_engine import BasicCLI, Command


@Command(name="build")
class BuildCLI(BasicCLI):
    def __init__(self, build_service: BuildService):
        self.build_service = build_service
    
    def execute(self):
        self.build_service.start_build()