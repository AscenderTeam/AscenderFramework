from ascender.clis.builder.build_service import BuildService
from ascender.core.cli.application import ContextApplication
from ascender.core.cli.main import BaseCLI


class BuildCLI(BaseCLI):
    def __init__(self, build_service: BuildService):
        self.build_service = build_service
    
    def callback(self, ctx: ContextApplication):
        self.build_service.start_build(ctx)