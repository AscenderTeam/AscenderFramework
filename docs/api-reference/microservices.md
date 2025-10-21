# Microservices API

The Microservices API provides utilities for building distributed microservice architectures with message-based communication.

## Core Components

::: ascender.common.microservices.ClientProxy
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Decorators

::: ascender.common.microservices.MessagePattern
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      members:
        - __init__


::: ascender.common.microservices.EventPattern
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      members:
        - __init__


## Transport Methods

::: ascender.common.microservices.instances.kafka.transporter.KafkaTransporter
    options:
      show_root_heading: true
      show_source: false
      members_order: source

::: ascender.common.microservices.instances.redis.transporter.RedisTransporter
    options:
      show_root_heading: true
      show_source: false
      members_order: source

::: ascender.common.microservices.instances.tcp.transporter.TCPTransporter
    options:
      show_root_heading: true
      show_source: false
      members_order: source


## Enums

::: ascender.common.microservices.Transports
    options:
      show_root_heading: true
      show_source: false
      show_labels: true
      members:
        - TCP
        - REDIS
        - NATS 
        - MQTT
        - RABBITMQ
        - KAFKA


::: ascender.common.microservices.types.transport.Transport
    options:
      show_root_heading: true
      show_source: true
      show_labels: false

## See Also

- [Microservices Guide](../microservices/getting-started.md) - Getting started with microservices
- [Message Patterns](../microservices/patterns.md) - Message pattern documentation
- [Transport Layer](../microservices/transports.md) - Transport layer details
