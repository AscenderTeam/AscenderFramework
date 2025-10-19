from typing import Annotated
from unittest import TestCase

from ascender.core.applications.application import Application
from ascender.core.di.inject import Inject
from ascender.core.di.injector import AscenderInjector
from ascender.core.di.interface.consts import CyclicDependency
from ascender.core.services import Service
from tests.di.examples.annotated_service import AnnotatedService
from tests.di.examples.circular_a_service import CircularAService
from tests.di.examples.circular_b_service import CircularBService
from tests.di.examples.did_service import DidService
from tests.di.examples.sample_service import SampleService
from tests.di.utils.examples.example_service import ExampleService


class TestInjector(TestCase):
    def test_basic_injection(self):
        """Test simple injection of a basic service."""
        root_injector = AscenderInjector([ExampleService])
        service = root_injector.get(ExampleService)

        self.assertIsInstance(
            service,
            ExampleService,
            "Injection failed: No object was returned for the ExampleService token!"
        )

    def test_dependency_injection(self):
        """Test injection with dependent services."""
        root_injector = AscenderInjector([
            {
                "provide": Application,
                "use_factory": lambda: "test",  # type: ignore
            },
            DidService
        ])
        service = root_injector.get(DidService)

        self.assertIsInstance(
            service,
            DidService,
            "Injection failed: No object was returned for the DidService token!"
        )

        self.assertEqual(
            service.application,  # type: ignore
            "test",
            "Comparison failed: Injected object is not an instance of Application!"
        )

    def test_annotated_injection(self):
        """Test injection with annotations."""
        root_injector = AscenderInjector([
            {"provide": "settings", "value": "Some value"},
            AnnotatedService
        ])
        service = root_injector.get(AnnotatedService)

        self.assertIsInstance(
            service,
            AnnotatedService,
            "Injection failed: No object was returned for the AnnotatedService token!"
        )

        self.assertEqual(
            service.some_settings,  # type: ignore
            "Some value",
            "Comparison failed: Injected value does not match expected!"
        )

    def test_nested_injection(self):
        """Test nested dependency injection."""
        root_injector = AscenderInjector([
            SampleService,
            {
                "provide": Application,
                "use_factory": lambda: "asd",  # type: ignore
            },
            {"provide": "settings", "value": "Some value"},
            DidService
        ])
        service = root_injector.get(SampleService)

        self.assertIsInstance(
            service,
            SampleService,
            "Injection failed: No object was returned for the SampleService token!"
        )

        self.assertEqual(
            service.some_settings,  # type: ignore
            "Some value",
            "Comparison failed: Injected value does not match expected!"
        )

        self.assertIsInstance(
            service.did_service,  # type: ignore
            DidService,
            "Comparison failed: Injected token is not an instance of DidService!"
        )

    def test_circular_injection(self):
        """Test detection of circular dependencies."""
        root_injector = AscenderInjector([CircularAService, CircularBService])
        
        with self.assertRaises(CyclicDependency, msg="Circular dependency was not detected!"):
            root_injector.get(CircularAService)
    
    def test_hierarchy_injection(self):
        root_injector = AscenderInjector([ExampleService])
        second_injector = AscenderInjector([], root_injector)

        self.assertIsInstance(second_injector.get(ExampleService), ExampleService, "Second Injector failed to inject it's parent's token!")

        # 3rd layered approach
        third_injector = AscenderInjector([], second_injector)
        self.assertIsInstance(third_injector.get(ExampleService), ExampleService, "Third Injector failed to inject it's parents' token! 3rd layered approach")
    
    def test_multi_injection(self):
        """Test multiple injection providers dependency injection."""
        # @Injectable()
        class SomeService(Service):
            def __init__(self, some_values: Annotated[list[str], Inject("SUPER_VALUE")]) -> None:
                self.some_values = some_values

        root_injector = AscenderInjector([
            SomeService,
            {"provide": "SUPER_VALUE", "value": "Some value", "multi": True},
            {"provide": "SUPER_VALUE", "value": "Some value 2", "multi": True},
        ])
        service = root_injector.get(SomeService)

        self.assertIsInstance(
            service,
            SomeService,
            "Injection failed: No object was returned for the SomeService token!"
        )

        self.assertIsInstance(service.some_values, list, "`some_values` which is multi dependency is not provided as list!") # type: ignore
        print(service.some_values)