# Testing

Ascender Framework provides a comprehensive testing system built on pytest, with utilities for dependency injection mocking, test lifecycle management, and data generation.

## Getting Started

### Installation

Tests are located in `src/tests/` by default. The framework provides built-in testing utilities through the `ascender.testing` module.

### Running Tests

Use the local CLI wrapper to run tests:

```bash
# Run all tests
ascender run tests

# Run with verbose output
ascender run tests --verbose

# Run with specific marks
ascender run tests -m "unit"
```

### Initialize Testing Environment

The framework can scaffold a basic testing environment (planned feature):

```bash
ascender run tests init
```

This command will:

- Create `src/tests/` directory structure
- Generate sample test files (`conftest.py`, `test_initial.py`)
- Create `pytest.ini` configuration file

---

## Test Configuration

### pytest.ini

The `pytest.ini` file configures pytest behavior:

```ini
[pytest]
testpaths = src/tests
python_files = test_*.py
python_classes = Test* *Tests
python_functions = test_*
addopts = -v --tb=short --disable-warnings
log_cli = true
log_level = INFO
asyncio_mode = auto
```

### conftest.py

The `conftest.py` file sets up the test lifecycle:

```python
import pytest
from ascender.testing import AscenderTestLifecycle

# Initialize lifecycle with your app module or providers
lifecycle = AscenderTestLifecycle(providers=[])

def pytest_sessionstart(session: pytest.Session):
    """Initialize framework at session start."""
    lifecycle.begin_session(session)

@pytest.fixture(scope="function", autouse=True)
def ascender_app():
    """Provide application instance to tests."""
    lifecycle.before_test()
    yield lifecycle.application
    lifecycle.after_test()

def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    """Cleanup at session end."""
    lifecycle.end_session()
```

---

## Testing Utilities

### AscenderTestLifecycle

Manages the test lifecycle and application initialization:

```python
from ascender.testing import AscenderTestLifecycle
from app_module import AppModule

# With app module
lifecycle = AscenderTestLifecycle(app_module=AppModule)

# With custom providers
lifecycle = AscenderTestLifecycle(providers=[
    MyService,
    # other providers...
])
```

### TestClient

Create test instances with mocked dependencies:

```python
from ascender.testing import TestClient, MockDependency
from controllers.user_controller import UserController
from services.user_service import UserService

def test_user_controller():
    # Mock the service
    controller = TestClient(
        UserController,
        mocks={
            UserService: MockDependency(
                get_user=lambda self, id: {"id": id, "name": "Test User"}
            )
        }
    )
    
    # Test the controller
    result = await controller.get_user(1)
    assert result["name"] == "Test User"
```

### Mixer

Generate test data for Pydantic models:

```python
from ascender.testing import Mixer, FakerField
from pydantic import BaseModel
from typing import Annotated

class User(BaseModel):
    name: str
    email: Annotated[str, FakerField("email")]
    age: int

# Create mixer
mixer = Mixer(enable_auto_faker=True)

# Generate single instance
user = mixer.blend(User)

# Generate multiple instances
users = mixer.blend_many(User, count=5)

# With overrides
user = mixer.blend(User, name="John Doe")
```

### MockDependency

Create mock objects for testing:

```python
from ascender.testing import MockDependency

# Create mock
mock_service = MockDependency(
    get_data=lambda self: "mocked data",
    process=lambda self, value: f"processed: {value}",
    config={"setting": "value"}
)

# Use as object
mock_obj = mock_service._as_object("MockService")
print(mock_obj.get_data())  # "mocked data"
```

---

## Writing Tests

### Basic Test Example

```python
from ascender.core import Application, inject, TestInjector

def test_application_boots(ascender_app: Application):
    """Test that application initializes correctly."""
    assert ascender_app.app is not None
    assert ascender_app.is_ok()
```

### Testing with Dependency Injection

```python
from ascender.core import inject
from services.my_service import MyService

def test_service_injection():
    """Test that services can be injected."""
    service = inject(MyService)
    assert isinstance(service, MyService)
```

### Testing Controllers

```python
from ascender.testing import TestClient, MockDependency
from controllers.user_controller import UserController
from services.user_service import UserService

def test_user_controller_get_all():
    """Test controller with mocked service."""
    controller = TestClient(
        UserController,
        mocks={
            UserService: MockDependency(
                get_all=lambda self: [
                    {"id": 1, "name": "User 1"},
                    {"id": 2, "name": "User 2"}
                ]
            )
        }
    )
    
    result = await controller.get_all_users()
    assert len(result) == 2
```

### Testing with Faker

```python
from ascender.testing import Mixer, FakerField
from typing import Annotated
from pydantic import BaseModel

class UserDTO(BaseModel):
    username: Annotated[str, FakerField("user_name")]
    email: Annotated[str, FakerField("email")]
    city: Annotated[str, FakerField("city")]

def test_user_creation():
    """Test user creation with generated data."""
    mixer = Mixer(enable_auto_faker=True)
    user_data = mixer.blend(UserDTO)
    
    # Data is automatically generated
    assert "@" in user_data.email
    assert len(user_data.username) > 0
```

---

## Testing Modules

Create isolated testing modules:

```python
from ascender.testing import TestClient
from ascender.core import inject

def test_module_creation():
    """Test creating a testing module."""
    module_ref = TestClient.create_testing_module(
        imports=[],
        declarations=[UserController],
        providers=[UserService],
        exports=[],
        name="TestModule"
    )
    
    # Use the injector to get dependencies
    service = inject(UserService, scope=module_ref)
    assert service is not None
```

---

## Best Practices

1. **Use Fixtures**: Leverage pytest fixtures for common setup
2. **Mock External Dependencies**: Use `MockDependency` for external services
3. **Test Isolation**: Each test should be independent
4. **Use Faker for Data**: Generate realistic test data with `Mixer`
5. **Test DI**: Verify dependency injection works correctly
6. **Async Tests**: Use `async def` for async endpoint tests
7. **Mark Tests**: Use pytest marks to organize tests (`@pytest.mark.unit`)

---

## Next Steps

- Explore [Dependency Injection](dependency-injection.md) for better understanding of DI testing
- Learn about [Controllers](controllers.md) to test endpoints effectively
- Check out pytest documentation for advanced testing patterns
