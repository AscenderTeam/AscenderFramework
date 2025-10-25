# Validation API

The Validation API provides base classes and utilities for request/response validation using Pydantic.

## Base Classes

### BaseDTO

::: ascender.common.base.dto.BaseDTO
    options:
      show_root_heading: true
      show_source: false

### BaseResponse

::: ascender.common.base.response.BaseResponse
    options:
      show_root_heading: true
      show_source: false

## Example Usage

### Basic DTO

```python
from ascender.common import BaseDTO
from pydantic import Field, EmailStr

class CreateUserDTO(BaseDTO):
    """Data transfer object for creating a user."""
    
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(...)
    age: int = Field(..., ge=18, le=120)
    bio: str | None = Field(None, max_length=500)
```

### Response Models

```python
from ascender.common import BaseResponse
from datetime import datetime

class UserResponse(BaseResponse):
    """User response model."""
    
    id: str
    name: str
    email: str
    age: int
    created_at: datetime
    updated_at: datetime

class UserListResponse(BaseResponse):
    """Paginated user list response."""
    
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
```

### Using in Controllers

```python
from ascender.common import Controller, GET, POST, Body
from ascender.common import inject

@Controller("/users")
class UserController:
    """User management endpoints."""
    
    def __init__(self, user_service=inject()):
        self.user_service = user_service
    
    @GET("/:id", response_model=UserResponse)
    async def get_user(self, id: str):
        """Get user by ID with validated response."""
        user = await self.user_service.find_by_id(id)
        return UserResponse(**user)
    
    @POST("/", response_model=UserResponse, status_code=201)
    async def create_user(self, data: CreateUserDTO = Body(...)):
        """Create user with validated input."""
        user = await self.user_service.create(data.model_dump())
        return UserResponse(**user)
    
    @GET("/", response_model=UserListResponse)
    async def list_users(self, page: int = 1, limit: int = 10):
        """List users with pagination."""
        users, total = await self.user_service.list(page, limit)
        return UserListResponse(
            users=[UserResponse(**u) for u in users],
            total=total,
            page=page,
            page_size=limit
        )
```

### Custom Validators

```python
from ascender.common import BaseDTO
from pydantic import Field, field_validator, model_validator

class CreateProductDTO(BaseDTO):
    """Product creation with custom validation."""
    
    name: str = Field(..., min_length=3)
    price: float = Field(..., gt=0)
    discount_price: float | None = Field(None, gt=0)
    category: str = Field(...)
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is in allowed list."""
        allowed = ['electronics', 'clothing', 'food', 'books']
        if v.lower() not in allowed:
            raise ValueError(f'Category must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @model_validator(mode='after')
    def validate_discount_price(self):
        """Validate discount price is less than regular price."""
        if self.discount_price and self.discount_price >= self.price:
            raise ValueError('Discount price must be less than regular price')
        return self
```

### Nested Models

```python
from ascender.common import BaseDTO, BaseResponse

class AddressDTO(BaseDTO):
    """Address information."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"

class CreateUserDTO(BaseDTO):
    """User with nested address."""
    name: str
    email: str
    address: AddressDTO
    
class AddressResponse(BaseResponse):
    """Address response."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str

class UserResponse(BaseResponse):
    """User response with nested address."""
    id: str
    name: str
    email: str
    address: AddressResponse
```

### Optional and Default Values

```python
from ascender.common import BaseDTO
from datetime import datetime

class UpdateUserDTO(BaseDTO):
    """Partial update with optional fields."""
    name: str | None = None
    email: str | None = None
    age: int | None = None
    bio: str | None = None
    updated_at: datetime = Field(default_factory=datetime.now)
```

### Configuration Options

```python
from ascender.common import BaseDTO
from pydantic import ConfigDict

class StrictUserDTO(BaseDTO):
    """DTO with custom configuration."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Strip whitespace from strings
        str_min_length=1,            # Minimum string length
        validate_assignment=True,     # Validate on attribute assignment
        extra='forbid',               # Forbid extra fields
        frozen=False,                 # Allow mutation
    )
    
    name: str
    email: str
```

## See Also

- [Data Validation Guide](../essentials/data-validation.md) - Comprehensive validation guide
- [Pydantic Documentation](https://docs.pydantic.dev/) - Official Pydantic docs
- [Controllers](controllers.md) - Using validation in controllers
