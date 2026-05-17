---
brief: 仓储模式通过接口抽象数据访问逻辑，使数据源可互换，便于测试和切换实现。
---

# Repository Pattern

> Source(s): raw/ch-03-Continuous Integration and Delivery

仓储模式（Repository Pattern）是软件设计中常见的数据访问抽象层。它将数据访问逻辑隐藏在接口之后，使业务代码无需关心底层数据源的具体实现——可以是关系型数据库、文档数据库、外部API，甚至是内存集合。这种解耦使得数据源可以互换，测试时也能轻松替换为内存实现或模拟对象（mock），从而提升代码的可测试性和可维护性。

设计模式是可重用的解决方案，用以解决软件设计中的常见问题，为开发人员提供讨论架构决策的共享词汇。仓储模式正是这样一种模式：它定义了统一的集合风格接口（如 `find()`、`save()`、`delete()`），业务层通过该接口操作数据，而不直接依赖 ORM 或数据库客户端。这种抽象在领域驱动设计（DDD）中尤为重要，它允许领域模型专注于业务逻辑，而将持久化责任完全交给仓储实现。

实际应用中，仓储模式常与依赖注入容器配合使用：容器负责在运行时注入具体的仓储实现（例如 `UserRepositoryPostgres` 或 `UserRepositoryInMemory`）。这种组合使得数据源切换（如从开发用 H2 数据库切换到生产用 PostgreSQL）只需修改配置代码，而不影响业务逻辑。同时，单元测试可以直接注入内存仓储，避免启动数据库或网络调用，大幅提升测试速度。

在持续集成（CI）背景下，仓储模式也帮助改善构建流程。使用内存仓储的测试无需依赖外部服务，因此更容易在 CI 管道中并行执行。结合测试金字塔（[[testing-pyramid]]），单元测试（使用模拟仓储）运行极快，可以频繁运行；而集成测试则使用真实数据库，运行次数较少但覆盖率更深。

## See also
- [[design-patterns]]
- [[factory-pattern]]
- [[singleton-pattern]]
- [[strategy-pattern]]
- [[observer-pattern]]
- [[dependency-injection]]
- [[unit-testing]]
- [[integration-testing]]
- [[continuous-integration]]
