from typing import ForwardRef
from unittest import TestCase
from ascender.core.applications.application import Application
from ascender.core.di.interface.provider import Provider
from ascender.core.di.utils.forward_ref import is_forward_ref, resolve_dep_forward_ref, resolve_forward_ref
from tests.di.utils.examples.example_service import ExampleService


class TestForwardRef(TestCase):
    def test_is_forward_ref(self):
        _forwardref = is_forward_ref(ForwardRef("ExampleService"))
        self.assertTrue(_forwardref, "`ExampleService` should be forward ref as specified in ForwardRef or str formats!")

        _wrong_forwardref = is_forward_ref(Application)
        self.assertFalse(_wrong_forwardref, "Application is type[Application] and can't be forward reference as is's original type itself!")
    
    # def test_resolve_froward_ref(self):
    #     _resolved_reference = resolve_forward_ref("ExampleService", globalns=globals(), localns=locals())
    #     self.assertIs(_resolved_reference, ExampleService, "Resolved type should be type of ExampleService!")

    #     _resolved_string_ref = resolve_forward_ref("Application")
    #     self.assertIs(_resolved_string_ref, Application, "Resolved type should be type of Application!")

    def test_dependency_forwardref(self):
        _resolved_string_reference = resolve_dep_forward_ref("ExampleService", [ExampleService])
        self.assertTrue(issubclass(_resolved_string_reference, ExampleService), "Resolved string is not Example Service. How odd...")

        _resolved_forward_ref = resolve_dep_forward_ref(ForwardRef("ExampleService"), [ExampleService])
        self.assertTrue(issubclass(_resolved_forward_ref, ExampleService), "Resolved forward reference is not `ExampleService`. How odd...")