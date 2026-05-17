---
brief: 装饰器模式动态地为对象附加额外职责，是子类化的灵活替代方案，Python装饰器是语言层面的实现，中间件管道也应用了该概念。
---

# Decorator Pattern

> Source(s): raw/ch-03-Continuous Integration and Delivery

装饰器模式（Decorator Pattern）是一种结构型设计模式，用于在不修改现有类的情况下动态地向对象添加新功能。它通过将对象包装在装饰器对象中，实现职责的灵活组合，是继承的替代方案之一。

## 核心思想

装饰器模式的核心是“开闭原则”（对扩展开放、对修改关闭）。原始对象和装饰器实现相同的接口，装饰器通过组合持有原始对象的引用，在调用原始方法前后添加新行为。多个装饰器可以层层嵌套，形成职责链。

## 与其他模式的关系

- **工厂模式**常与装饰器模式配合，由工厂创建装饰链。
- **策略模式**允许算法互换，而装饰器专注于增强对象行为。
- **管道（Pipeline）** 概念（如中间件管道、CI/CD流水线）本质上也是一种装饰器思想：每个阶段处理输入并传递给下一阶段，类似装饰器模式的责任链变体。

## 语言层面的实现

Python 中的 `@decorator` 语法是装饰器模式的直接体现，允许函数或类在不修改定义的情况下被包装。例如：

```python
def log(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log
def greet(name):
    return f"Hello, {name}"
```

其他语言如 Java 通过 `BufferedReader`（装饰 `Reader`）或 `Collections.synchronizedList` 等标准库实现装饰器模式。现代框架（如 NestJS、Express 中间件）也广泛采用该模式。

## 在 CI/CD 中的体现

在持续集成与交付中，**Pipeline as Code**（如 `.github/workflows/*.yml`）中的工作流步骤本质上可以看作一个装饰器链：每个步骤（checkout、build、test、report）装饰前一步的结果，添加验证或转换逻辑。同样，中间件模式（如消息队列、API 网关）通过装饰请求/响应来实现日志、鉴权、限流等功能。

## 优点与缺点

**优点**：
- 比继承更灵活，可在运行时动态添加或移除职责。
- 避免类爆炸（多个特性组合无需定义子类）。
- 符合单一职责原则，每个装饰器只关注一个功能。

**缺点**：
- 多层装饰会增加系统复杂度，调试困难。
- 装饰器顺序可能影响结果，需要谨慎设计。
- 不易于进行与装饰器本身无关的测试。

## See also
- [[factory-pattern]]
- [[strategy-pattern]]
- [[pipeline-as-code]]
- [[design-patterns]]
- [[system-architecture]]
