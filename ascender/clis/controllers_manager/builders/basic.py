import os
import inflection
from ascender.clis.controllers_manager.builder import ControllerBuilder
from ascender.clis.controllers_manager.loader import TLoader


class BasicBuilder(ControllerBuilder):

    def prepare_placeholders(self) -> dict[str, str]:
        camelized_name = inflection.camelize(self.name.replace(' ', '_'))
        underscored_name = self.name.lower().replace(' ', '_')
        controller_namespace = os.path.splitext(self.controller_dir)[0].replace(os.sep, '.')
        controller_lowered = inflection.underscore(camelized_name)

        base_pl = {
            "controller": camelized_name,
            "service": f"{camelized_name}Service",
            "repository": f"{camelized_name}Repo"
        }
        metadata_pl = {
            "controller_namespace": f"{controller_namespace}.{underscored_name}",
            "services_di": f"{controller_lowered}_service: {base_pl['service']},",
            "service_definition": f"self.{controller_lowered}_service = {controller_lowered}_service",
            "service_definition_secondary": f"\"{controller_lowered}_service\": {base_pl['service']}",
            "service_name": f"{controller_lowered}"
        }

        return {**base_pl, **metadata_pl}

    def build(self, extra_dirs: bool) -> dict[str, str]:
        template_placeholders = self.prepare_placeholders()

        template_loader = TLoader("basic", **template_placeholders)
        template_loader.load_structure(True)
        template_loader.load_template(f"{self.controller_dir}/{self.name}")
        return template_loader.structure_memory