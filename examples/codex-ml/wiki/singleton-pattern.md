---
brief: 单例模式确保一个类只有一个实例并提供全局访问点，但因隐藏依赖和妨碍测试而逐渐被依赖注入容器替代
---

# Singleton Pattern

> Source(s): raw/ch-03-Continuous Integration and Delivery

The Singleton pattern ensures a class has only one instance and provides a global point of access. While once widely used, it has fallen out of favor in modern software design due to its tendency to create hidden dependencies and complicate testing. Singletons introduce implicit coupling and make code harder to test because they maintain global state that persists across tests.

Modern alternatives include dependency injection (DI) containers that manage object lifecycles explicitly. DI allows developers to configure singleton-like behavior (e.g., a single shared instance) without global access, making dependencies visible and testable. In test code, singletons can be replaced by providing test-specific instances through the DI framework, enabling isolated unit tests that don't rely on shared state.

The decline of the Singleton pattern reflects a broader shift toward explicit dependency management and testability. Teams practicing Continuous Integration and trunk-based development benefit from reducing hidden couplings that can cause flaky tests and integration delays.

## See also
- [[factory-pattern]]
- [[repository-pattern]]
- [[dependency-injection]]
