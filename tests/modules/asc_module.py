from typing import Any, cast
from unittest import TestCase

from ascender.core.applications.application import Application
from ascender.core.applications.root_injector import RootInjector
from ascender.core.di.injector import AscenderInjector
from ascender.core.di.none_injector import NoneInjectorException
from ascender.core.struct.module import AscModule
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.utils.module import load_module
from tests.di.examples.annotated_service import AnnotatedService
from tests.di.examples.did_service import DidService
from tests.di.examples.sample_service import SampleService
from tests.di.utils.examples.example_service import ExampleService
from tests.modules.example.first_module import FirstModule
from tests.modules.example.first_service import FirstService
from tests.modules.example.second_module import SecondModule
from tests.modules.example.third_module import ThirdModule


class TestAscModule(TestCase):
    def setUp(self):
        root_injector = RootInjector()
        root_injector.create([])
    
    def test_module_load(self):
        try:
            first_module = load_module(FirstModule)
        except RuntimeError: # In case if one of tests loaded module we should ignore `module already loaded` exeption
            first_module = FirstModule

        self.assertTrue(hasattr(first_module, "_injector"), "Loaded module lacks of injector, which means module load failed!")
        self.assertIsInstance(
            first_module._injector, AscenderInjector, 
            f"Module's injector is not an AscenderInjector... Then what is it? Is that {type(first_module._injector)}??"
        )

    def test_dependency_injection(self):
        first_module = load_module(FirstModule)
        first_service = first_module._injector.get(FirstService)

        self.assertIsInstance(
            first_service.example_service, ExampleService, 
            f"Dependency injection failed: Required dependency in `first_service.example_service` wasn't what we expected"
        )
    
    def test_encapsulation(self):
        second_module = load_module(SecondModule)
        with self.assertRaises(NoneInjectorException, msg="Encapsulation failed, `FirstModule` let `SecondModule` to import it's tokens without `exports` permission"):
            second_module._injector.get(FirstService)
    
    def test_imports(self):
        third_module = load_module(ThirdModule)
        example_service = third_module._injector.get(ExampleService) # Importing provider which's not defined in `ThridModule` but was defined & exported in `SecondModule`

        self.assertIsInstance(
            example_service, ExampleService,
            f"Dependency injection failed: Required dependency in `example_service` wasn't what we expected"
        )