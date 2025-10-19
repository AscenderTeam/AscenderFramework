# Overview
---
## Microservices Module Overview

!!! warning
    This feature is right now in pre-release state. It's still raw and unfinished, please use it on your own risk.
    Early access only

The microservices module in Ascender Framework provides a structured way to build scalable, distributed applications using an event-driven architecture. Inspired by [NestJS](https://docs.nestjs.com/microservices/basics), it allows services to communicate asynchronously via event patterns, message patterns, and RPC calls.

At its core, the module facilitates inter-service communication through event emitting and message-based interactions, enabling decoupled components to work seamlessly. This approach enhances modularity, fault tolerance, and scalability while maintaining a clean separation of concerns between services.

Microservices in Ascender Framework can be deployed independently, communicate through various transport layers (such as Kafka, Redis, and HTTP), and handle distributed workloads efficiently. The built-in service discovery mechanism ensures that events and messages are properly routed, allowing developers to focus on business logic without worrying about communication complexities.

With this module, developers can create highly maintainable, event-driven architectures while leveraging the power of Ascender Framework’s dependency injection and modular structure.

In addition, data serialization and conversion of [DTO](/essentials/data-validation#defining-dtos), [Response](/essentials/data-validation#defining-responses) models will be handled on Ascender Framework's Microservice module's side.



## Learn more about Ascender Framework's dependency injection
