from ascender.clis.builder.build_message_service import BuildMessageService
from ascender.core import Service
from ascender.common import Injectable
from ascender.core._builder.file_builder import build_file_manager
from ascender.core._builder.minifier import minify_project
from ascender.core._builder.obfuscator import obfuscate_project
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core.cli.application import ContextApplication


@Injectable(provided_in="root")
class BuildService(Service):
    def __init__(self, build_message_service: BuildMessageService):
        self.build_message_service = build_message_service

    def get_configs(self):
        return _AscenderConfig().config

    def start_build(self, ctx: ContextApplication):
        configs = self.get_configs()
        build_configs = configs.build
        
        self.build_message_service.display_start_message(ctx, configs.project["name"])

        if build_configs.obfuscate:
            self.build_message_service.display_obfuscation_start(ctx)
            self.build_file_manager(False)
            obfuscate_project(
                configs.project["name"], configs.paths.output, configs.paths.source
            )

            self.build_message_service.display_obfuscation_finished(ctx, f"{configs.paths.output}/{configs.project['name']}")
            self.build_message_service.display_obfuscated_instructions(ctx)
            return

        if build_configs.minify:
            self.build_message_service.display_minification_start(ctx)
            self.build_file_manager(False)
            minify_project(
                configs.project["name"], 
                configs.paths.output, 
                configs.paths.source, 
                build_configs.stripComments
            )
            self.build_message_service.display_minification_finished(ctx, f"{configs.paths.output}/{configs.project['name']}")
            return
        
        self.build_file_manager(True)
        self.build_message_service.display_finish_message(ctx, f"{configs.paths.output}/{configs.project['name']}")

    def build_file_manager(self, use_source: bool = True):
        configs = self.get_configs()
        build_configs = configs.build

        return build_file_manager(
            configs.project["name"], configs.paths.output, configs.project.get(
                "version", "0.1.0"
            ),
            None if not use_source else configs.paths.source,
            configs.paths.static if build_configs.includeStatic else None
        )
