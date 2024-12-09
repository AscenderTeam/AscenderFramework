import os
import inflection
from ascender.clis.controllers_manager.builder import ControllerBuilder
from ascender.clis.controllers_manager.errors.improper_namespace import ImproperNamespaceError
from ascender.clis.controllers_manager.loader import TLoader
from ascender.core.database.types.orm_enum import ORMEnum


class AuthBuilder(ControllerBuilder):
    def __init__(self, name: str, controller_dir: str, orm_type: ORMEnum,
                 entity_module: str) -> None:
        super().__init__(name, controller_dir)
        self.entity_module = entity_module
        self.orm_type = orm_type
    
    def prepare_placeholders(self) -> dict[str, str]:
        if len(self.entity_module.split(".")) < 2:
            raise ImproperNamespaceError("Incorrect entity namespace, should be `file.EntityClass` from `entities/`. Example: `users.UserEntity`")
        
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
            "service_lowered": f"{controller_lowered}_service",
            "services_di": f"{controller_lowered}_service: {base_pl['service']},",
            "service_definition": f"self.{controller_lowered}_service = {controller_lowered}_service",
            "service_definition_secondary": f"\"{controller_lowered}_service\": {base_pl['service']}"
        }
        entity_pl = {
            "entity_namespace": "entities." + self.entity_module.split(".")[0],
            "user_entity": self.entity_module.split(".")[1]
        }

        return {**base_pl, **metadata_pl, **entity_pl}

    def build(self, extra_dirs: bool) -> dict[str, str]:
        template_placeholders = self.prepare_placeholders()

        template_loader = TLoader("auth", **template_placeholders)
        template_loader.add_pathpoint(self.orm_type.value)
        
        template_loader.load_structure(True)
        template_loader.load_template(f"{self.controller_dir}/{self.name}")
        return template_loader.structure_memory