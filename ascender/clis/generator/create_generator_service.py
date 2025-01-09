from importlib import import_module
import os
from typing import Any, Literal
from ascender.clis.generator.edit_generator_service import EditGeneratorService
from ascender.common.injectable import Injectable
from ascender.core.services import Service
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.schematics.controller.create import ControllerCreator
from ascender.schematics.guard.create import GuardCreator
from ascender.schematics.module.create import ModuleCreator
from ascender.schematics.repository.create import RepositoryCreator
from ascender.schematics.service.create import ServiceCreator
from ascender.schematics.utilities.case_filters import pascal_case
from ascender.schematics.utilities.namespace_maker import path_to_namespace


@Injectable(provided_in="root")
class CreateGeneratorService(Service):
    def __init__(
        self, 
        edit_generator_service: EditGeneratorService
    ):
        self.edit_generator_service = edit_generator_service
    
    def generate_controller(
        self, 
        name: str,
        standalone: bool,
        prefix: str,
        suffix: str,
        module: str | None = None,
    ):
        controller_creator = ControllerCreator(name, standalone, prefix, suffix)
        
        # Creates and also returns information about file state
        file_info = controller_creator.invoke()

        post_processing_metadata = controller_creator.post_processing()

        # Process the post processing metdata to extract useful information about controller
        controller_path: str = file_info["file_path"]

        # Data for import is collected >_o
        controller_class_name = pascal_case(post_processing_metadata["controller_name"]) + "Controller"
        controller_package = path_to_namespace(controller_path)

        # Check if standalone and if not, then add it into module if specified
        module_update = None
        if not standalone and module:
            module_update = self.edit_generator_service.update_module(
                parent_path=os.path.dirname(os.path.abspath(controller_path)),
                name=name,
                package_imports={controller_package: controller_class_name},
                imports=[],
                providers=[],
                declarations=[controller_class_name]
            )
        
        return module_update, file_info
    
    def generate_service(
        self, 
        name: str,
        module: str | None = None,
    ):
        service_creator = ServiceCreator(name)
        
        # Creates and also returns information about file state
        file_info = service_creator.invoke()

        post_processing_metadata = service_creator.post_processing()

        # Process the post processing metdata to extract useful information about controller
        service_path: str = file_info["file_path"]

        # Data for import is collected >_o
        service_class_name = pascal_case(post_processing_metadata["service_name"]) + "Service"
        service_package = path_to_namespace(service_path)

        # Check if standalone and if not, then add it into module if specified
        module_update = None
        if module:
            module_update = self.edit_generator_service.update_module(
                parent_path=os.path.dirname(os.path.abspath(service_path)),
                name=module,
                package_imports={service_package: service_class_name},
                imports=[],
                declarations=[],
                providers=[service_class_name]
            )
        
        return module_update, file_info
    
    def generate_module(
        self, 
        name: str,
        module: str | None = None
    ):
        module_creator = ModuleCreator(name, imports=[], providers=[], declarations=[])
        
        # Creates and also returns information about file state
        file_info = module_creator.invoke()
        
        post_processing_metadata = module_creator.post_processing()

        # Process the post processing metdata to extract useful information about controller
        module_path: str = file_info["file_path"]

        # Data for import is collected >_o
        module_class_name = pascal_case(post_processing_metadata["module_name"]) + "Module"
        module_package = path_to_namespace(module_path)

        module_update = None
        if module:
            module_update = self.edit_generator_service.update_module(
                parent_path=os.path.dirname(os.path.abspath(module_path)),
                name=module,
                package_imports={
                    module_package: module_class_name,
                },
                imports=[module_class_name],
                declarations=[],
                providers=[]
            )

        return module_update, file_info
    
    def generate_repository(
        self,
        name: str,
        entities: tuple[str],
        orm_mode: ORMEnum,
        module: str
    ):
        entities_d: dict[str, Any] = {}

        for entity in entities:
            # NOTE: Parses only this type of string, may raise error if it doesn't comply this type `entities.test:TestEntity`
            try:
                import_path, entity_name = entity.split(":")
                package = import_module(import_path)

                if not hasattr(package, entity_name):
                    raise ValueError("Entities format validations failed to pass!")
                entities_d[import_path] = getattr(package, entity_name)
            except Exception as e:
                print(e)
                # raise ValueError("Entities format validations failed to pass!")
                raise e
        
        if os.path.exists(os.path.abspath(f"{name.lower()}_repository.py")):
            return self.edit_generator_service.update_repository(name, entities_d, orm_mode)
        
        repository_creator = RepositoryCreator(name, entities_d, orm_mode)
        
        # Creates and also returns information about file state
        file_info = repository_creator.invoke()

        post_processing_metadata = repository_creator.post_processing()

        # Process the post processing metdata to extract useful information about controller
        repository_path: str = file_info["file_path"]

        # Data for import is collected >_o
        repository_class_name = pascal_case(post_processing_metadata["repository_name"]) + "Repo"
        repository_package = path_to_namespace(repository_path)

        # Check if standalone and if not, then add it into module if specified
        module_update = None
        if module:
            module_update = self.edit_generator_service.update_module(
                parent_path=os.path.dirname(os.path.abspath(repository_path)),
                name=module,
                package_imports={
                    repository_package: repository_class_name,
                    "ascender.core.utils.repository": "provideRepository",
                },
                imports=[],
                providers=[f"provideRepository({repository_class_name})"],
                declarations=[]
            )
        
        return module_update, file_info
    
    def generate_guard(
        self,
        name: str,
        guard_type: Literal["single", "parametrized"] = "single",
        guards: list[str] = [],
        module: str | None = None
    ):
        guard_creator = GuardCreator(name, guard_type, guards)
        
         # Creates and also returns information about file state
        file_info = guard_creator.invoke()

        post_processing_metadata = guard_creator.post_processing()

        # Process the post processing metdata to extract useful information about controller
        guard_path: str = file_info["file_path"]

        # Data for import is collected >_o
        guard_class_name = pascal_case(post_processing_metadata["guard_name"]) + "Guard"
        guard_package = path_to_namespace(guard_path)

        # Check if standalone and if not, then add it into module if specified
        module_update = None
        if module:
            module_update = self.edit_generator_service.update_module(
                parent_path=os.path.dirname(os.path.abspath(guard_path)),
                name=module,
                package_imports={
                    guard_package: guard_class_name,
                },
                imports=[],
                providers=[],
                declarations=[guard_class_name]
            )

        return module_update, file_info