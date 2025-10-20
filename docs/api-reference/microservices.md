# Microservices API

The Microservices API provides utilities for building distributed microservice architectures with message-based communication.

## Core Components

### ClientProxy

Client for sending messages and events to microservices.

**Constructor:**
```python
ClientProxy(
    transport: str = "redis",
    options: dict[str, Any] | None = None
)
```

**Parameters:**
- `transport`: Transport type (`"redis"`, `"kafka"`, `"rabbitmq"`)
- `options`: Transport-specific configuration options

**Key Methods:**
- `send(pattern: str, data: Any) -> Any`: Send request and wait for response
- `emit(pattern: str, data: Any) -> None`: Fire-and-forget event emission

**Usage:**
```python
from ascender.common.microservices import ClientProxy

client = ClientProxy(
    transport="redis",
    options={"host": "localhost", "port": 6379}
)

# Request-response
result = await client.send("user.create", {"name": "John"})

# Fire-and-forget event
await client.emit("user.created", {"id": "123"})
```

### MessageContext

Context object for message handlers containing metadata.

**Properties:**
- `correlation_id`: Unique identifier for request-response correlation
- `reply_to`: Pattern to reply to for request-response
- `headers`: Message headers/metadata
- `pattern`: The message pattern that was matched

**Usage:**
```python
from ascender.core import Controller
from ascender.common.microservices import MessageContext, MessagePattern

@Controller()
class MessageController:
    @MessagePattern("task.process")
    async def handle_task(self, data: dict, context: MessageContext):
        print(f"Correlation ID: {context.correlation_id}")
        print(f"Headers: {context.headers}")
        return {"status": "processed"}
```

### @MessagePattern Decorator

Decorator for handling request-response microservice messages.

**Signature:**
```python
@MessagePattern(pattern: str)
```

**Parameters:**
- `pattern`: Message pattern to match (e.g., `"user.create"`, `"order.*"`)

**Usage:**
```python
@Controller()
class UserServiceController:
    @MessagePattern("user.create")
    async def create_user(self, data: dict, context: MessageContext):
        # Handle user creation
        return {"success": True, "user_id": "123"}
```

### @EventPattern Decorator

Decorator for handling fire-and-forget event messages.

**Signature:**
```python
@EventPattern(pattern: str)
```

**Parameters:**
- `pattern`: Event pattern to match

**Usage:**
```python
@Controller()
class EventListeners:
    @EventPattern("user.created")
    async def on_user_created(self, data: dict, context: MessageContext):
        # Handle user created event
        print(f"User {data['id']} was created")
```

## Example Usage

### Creating a Microservice Client

```python
from ascender.common import Injectable
from ascender.common.microservices import ClientProxy

@Injectable()
class UserMicroserviceClient:
    """Client for User microservice."""
    
    def __init__(self):
        self.client = ClientProxy(
            transport="redis",
            options={
                "host": "localhost",
                "port": 6379,
                "db": 0
            }
        )
    
    async def create_user(self, user_data: dict):
        """Create user via microservice."""
        return await self.client.send(
            pattern="user.create",
            data=user_data
        )
    
    async def get_user(self, user_id: str):
        """Get user via microservice."""
        return await self.client.send(
            pattern="user.get",
            data={"id": user_id}
        )
    
    async def notify_user_created(self, user_data: dict):
        """Emit user created event (fire and forget)."""
        await self.client.emit(
            pattern="user.created",
            data=user_data
        )
```

### Microservice Message Handlers

```python
from ascender.common import Controller
from ascender.common.microservices import MessageContext, MessagePattern, EventPattern

@Controller()
class UserMicroserviceController:
    """Microservice controller for user operations."""
    
    def __init__(self, user_service=inject()):
        self.user_service = user_service
    
    @MessagePattern("user.create")
    async def handle_create_user(self, data: dict, context: MessageContext):
        """Handle user creation request."""
        user = await self.user_service.create(data)
        return {"success": True, "user": user}
    
    @MessagePattern("user.get")
    async def handle_get_user(self, data: dict, context: MessageContext):
        """Handle get user request."""
        user = await self.user_service.find_by_id(data["id"])
        if not user:
            return {"success": False, "error": "User not found"}
        return {"success": True, "user": user}
    
    @EventPattern("user.created")
    async def handle_user_created_event(self, data: dict, context: MessageContext):
        """Handle user created event."""
        # Send welcome email, update analytics, etc.
        print(f"User created: {data}")
```

### Request-Response Pattern

```python
from ascender.common.microservices import ClientProxy

class OrderService:
    """Order service that communicates with other services."""
    
    def __init__(self):
        self.user_client = ClientProxy(transport="redis")
        self.inventory_client = ClientProxy(transport="redis")
        self.payment_client = ClientProxy(transport="redis")
    
    async def create_order(self, order_data: dict):
        """Create order with distributed transaction."""
        
        # 1. Validate user
        user_response = await self.user_client.send(
            pattern="user.validate",
            data={"user_id": order_data["user_id"]}
        )
        if not user_response["valid"]:
            raise ValueError("Invalid user")
        
        # 2. Check inventory
        inventory_response = await self.inventory_client.send(
            pattern="inventory.reserve",
            data={"items": order_data["items"]}
        )
        if not inventory_response["available"]:
            raise ValueError("Items not available")
        
        # 3. Process payment
        payment_response = await self.payment_client.send(
            pattern="payment.charge",
            data={
                "user_id": order_data["user_id"],
                "amount": order_data["total"]
            }
        )
        if not payment_response["success"]:
            # Rollback inventory reservation
            await self.inventory_client.send(
                pattern="inventory.release",
                data={"reservation_id": inventory_response["reservation_id"]}
            )
            raise ValueError("Payment failed")
        
        # 4. Create order
        return {"order_id": "123", "status": "completed"}
```

### Event-Driven Architecture

```python
from ascender.common.microservices import ClientProxy, EventPattern

class EventPublisher:
    """Service for publishing domain events."""
    
    def __init__(self):
        self.client = ClientProxy(transport="redis")
    
    async def publish_user_registered(self, user: dict):
        """Publish user registered event."""
        await self.client.emit(
            pattern="user.registered",
            data={
                "user_id": user["id"],
                "email": user["email"],
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def publish_order_completed(self, order: dict):
        """Publish order completed event."""
        await self.client.emit(
            pattern="order.completed",
            data={
                "order_id": order["id"],
                "user_id": order["user_id"],
                "total": order["total"],
                "timestamp": datetime.now().isoformat()
            }
        )

# Event listeners
@Controller()
class EventListeners:
    """Listeners for domain events."""
    
    @EventPattern("user.registered")
    async def on_user_registered(self, data: dict, context: MessageContext):
        """Handle user registered event."""
        # Send welcome email
        print(f"Sending welcome email to user {data['user_id']}")
    
    @EventPattern("order.completed")
    async def on_order_completed(self, data: dict, context: MessageContext):
        """Handle order completed event."""
        # Update analytics, send confirmation email
        print(f"Order {data['order_id']} completed")
```

### Kafka Transport

```python
from ascender.common.microservices import ClientProxy

class KafkaService:
    """Service using Kafka transport."""
    
    def __init__(self):
        self.client = ClientProxy(
            transport="kafka",
            options={
                "brokers": ["localhost:9092"],
                "group_id": "user-service",
                "client_id": "user-service-client"
            }
        )
    
    async def publish_event(self, topic: str, event: dict):
        """Publish event to Kafka topic."""
        await self.client.emit(
            pattern=topic,
            data=event
        )
    
    async def request_response(self, topic: str, request: dict):
        """Send request and wait for response."""
        return await self.client.send(
            pattern=topic,
            data=request
        )
```

### Message Context Usage

```python
from ascender.common.microservices import MessageContext, MessagePattern

@Controller()
class MessageController:
    """Controller demonstrating message context usage."""
    
    @MessagePattern("task.process")
    async def process_task(self, data: dict, context: MessageContext):
        """Process task with context metadata."""
        
        # Access message metadata
        print(f"Correlation ID: {context.correlation_id}")
        print(f"Reply pattern: {context.reply_to}")
        print(f"Headers: {context.headers}")
        
        # Process task
        result = await self.do_work(data)
        
        # Return response (will be sent to reply_to pattern)
        return {
            "success": True,
            "result": result,
            "processed_at": datetime.now().isoformat()
        }
```

## Transport Options

### Redis Transport
```python
ClientProxy(
    transport="redis",
    options={
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": "secret"
    }
)
```

### Kafka Transport
```python
ClientProxy(
    transport="kafka",
    options={
        "brokers": ["localhost:9092"],
        "group_id": "my-service",
        "client_id": "my-client"
    }
)
```

### RabbitMQ Transport
```python
ClientProxy(
    transport="rabbitmq",
    options={
        "host": "localhost",
        "port": 5672,
        "username": "guest",
        "password": "guest",
        "virtual_host": "/"
    }
)
```

## See Also

- [Microservices Guide](../microservices/getting-started.md) - Getting started with microservices
- [Message Patterns](../microservices/patterns.md) - Message pattern documentation
- [Transport Layer](../microservices/transports.md) - Transport layer details
