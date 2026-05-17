---
brief: 设计模式是软件设计中常见问题的可复用解决方案，1994年由Gang of Four首次编目，提供架构决策的共享工程词汇。
---

# Design Patterns

> Source(s): raw/ch-03-Continuous Integration and Delivery

Design patterns are reusable solutions to common problems in software design. First cataloged by the Gang of Four (GoF) in 1994, design patterns provide a shared vocabulary for developers to discuss architectural decisions. While some patterns have become less relevant with language evolution, many remain fundamental to building maintainable, extensible software. Understanding when and how to apply patterns is a key skill for senior developers.

## Common Patterns

### Singleton
The Singleton pattern ensures a class has only one instance and provides a global point of access. While once popular, it has fallen out of favor due to its tendency to create hidden dependencies and complicate testing. Modern alternatives include dependency injection containers that manage object lifecycles explicitly. In test code, singletons can be replaced by providing test-specific instances through the dependency injection framework.

### Factory Method and Abstract Factory
The Factory Method and Abstract Factory patterns encapsulate object creation logic. Instead of calling constructors directly, client code calls factory methods that return appropriately configured objects. This decoupling allows the factory to choose which concrete class to instantiate based on configuration, environment, or other runtime factors. Factories are particularly useful in plugin architectures and when working with cross-platform abstractions.

### Observer
The Observer pattern defines a one-to-many dependency between objects: when one object changes state, all its dependents are notified automatically. This pattern underlies event-driven architectures, reactive programming frameworks, and publish-subscribe messaging systems. In modern JavaScript, the Observer pattern appears in the form of event listeners and the Observable pattern used by RxJS. In backend systems, message brokers like RabbitMQ and Kafka implement publish-subscribe at scale.

### Strategy
The Strategy pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable. This allows the algorithm to vary independently from clients that use it. Dependency injection of function objects enables flexible swapping of behavior at runtime.

## See also
- [[continuous-integration]]
- [[trunk-based-development]]
- [[pipeline-as-code]]
- [[code-review]]
- [[integration-testing]]
- [[unit-testing]]
