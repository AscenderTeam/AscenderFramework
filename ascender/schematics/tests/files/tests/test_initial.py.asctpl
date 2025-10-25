from ascender.core import Application, inject, TestInjector
from rich import print as rprint


def test_initial(ascender_app: Application):
    """
    Test to ensure that the Ascender Framework application boots up correctly.
    """
    assert ascender_app.app is not None
    rprint("✅ Application instance created successfully.")

    assert ascender_app.is_ok()
    rprint("✅ Dependency injection is properly configured.")

    assert isinstance(ascender_app.cli_settings, list)
    rprint("✅ CLI settings are properly configured.")


def test_injector():
    """
    Test to ensure that the dependency injector (on scope of testing) is functioning correctly.
    """
    injector = inject(TestInjector)
    rprint("✅ Dependency injector is accessible.")
    
    assert isinstance(injector, TestInjector)
    rprint("✅ Injector is of type TestInjector.")