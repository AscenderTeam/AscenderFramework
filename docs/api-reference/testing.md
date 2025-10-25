# Testing API

The Testing API provides utilities for testing Ascender Framework applications with pytest integration.

## Core Components

### Ascender Test Lifecycle

Manages the lifecycle of Ascender applications in test environments.

**Key Methods:**
- `before_all()`: Initialize application before test suite
- `after_all()`: Cleanup after all tests complete  
- `before_each()`: Setup before each test
- `after_each()`: Cleanup after each test

**Usage:**
```python
import pytest
from ascender.testing import AscenderTestLifecycle

@pytest.fixture(scope="session")
async def app():
    app = await create_application()
    lifecycle = AscenderTestLifecycle(app)
    await lifecycle.before_all()
    yield app
    await lifecycle.after_all()
```

::: ascender.testing.AscenderTestLifecycle
    options:
      show_root_heading: true
      show_source: false
      members_order: source

::: ascender.testing.TestClient
    options:
      show_root_heading: true
      show_source: false
      members_order: source

::: ascender.testing.Mixer
    options:
      show_root_heading: true
      show_source: false
      members_order: source

::: ascender.testing.FakerField
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__

::: ascender.testing.MockDependency
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Example Usage

### Basic Test Setup

```python
# src/tests/conftest.py
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
```

### Testing Controllers

```python
# tests/test_user_controller.py
import pytest
from ascender.testing import TestClient, MockDependency, Mixer

from controllers.user_controller import UserController
from controllers.user_service import UserService

from dtos.users import UserDTO
from responses.users import UserResponse


@pytest.fixture
def client():
    client = TestClient(UserController, {
        UserService: MockDependency(
            find_by_id=lambda self, user_id: UserResponse(id=user_id, name="Test User"),
            create=lambda self, data: UserResponse(id=1, **data.model_dump())
        )
    })
    yield client

@pytest.mark.asyncio
async def test_get_user(client: UserController):
    """Test getting a user by ID."""
    response = await client.get_user(id=223)
    
    assert isinstance(response, UserResponse)
    assert response.id == 223

@pytest.mark.asyncio
async def test_create_user(client: UserController):
    """Test creating a new user."""
    response = await client.create_user(data=Mixer(enable_auto_faker=True).blend(UserDTO))
    
    assert response.status_code == 201
    assert "id" in response.json()
```

### Using Mixer for Data Generation

```python
from ascender.testing import Mixer, FakerField
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int

# Generate random user data
user_data = Mixer().blend(User)
print(user_data)  # User(name='John Doe', email='john@example.com', age=25)

# Generate with specific fields
user = Mixer().blend(User, name="Alice", age=30)
print(user)  # User(name='Alice', email='alice@example.com', age=30)

# Use Faker for specific patterns
class Product(BaseModel):
    name: str = FakerField("company")
    price: float = FakerField("pydecimal", left_digits=3, right_digits=2)

product = Mixer().blend(Product)

products = Mixer().blend_many(Product, 5)

print(len(products))  # 5

mixed = Mixer().blend_multiple([User, Product], count=3)

print(mixed)  # List of mixed User and Product instances
print(len(mixed)) # 3
```

## Running Tests

```bash
# Run all tests
ascender run tests run

# Run specific test file
ascender run tests run --path src/tests/test_user_controller.py

# Run specific mark
ascender run tests run -m asyncio

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest src/tests/test_user_controller.py::test_get_user
```

You can use either `ascender run tests run` or `pytest` directly to execute your tests.

## See Also

- [Testing Guide](../essentials/testing.md) - Comprehensive testing guide
- [Test Client Documentation](../testing/test-client.md) - Detailed TestClient usage
- [Dependency Injection](di.md) - DI system for testing
