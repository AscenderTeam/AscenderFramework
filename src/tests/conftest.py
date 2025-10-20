import pytest
from ascender.testing import AscenderTestLifecycle


lifecycle = AscenderTestLifecycle(providers=[])


def pytest_sessionstart(session: pytest.Session):
    """
    Initialize Ascender Framework testing lifecycle at the start of the pytest session.
    """
    lifecycle.begin_session(session)


@pytest.fixture(scope="function", autouse=True)
def ascender_app():
    """
    Lifecycle-managed Ascender Framework test fixture.
    Automatically runs before and after each test function.
    """
    lifecycle.before_test()
    
    yield lifecycle.application
    
    lifecycle.after_test()
    

def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    """
    Finalize Ascender Framework testing lifecycle at the end of the pytest session.
    """
    lifecycle.end_session()