---
brief: 策略模式定义一族可互换的算法并分别封装，使算法可独立于使用它的客户端变化，在现代语言中通过函数对象或Lambda可实现更轻量的形式。
---

# Strategy Pattern

> Source(s): raw/ch-03-Continuous Integration and Delivery

Strategy pattern is a behavioral design pattern that defines a family of algorithms, encapsulates each one, and makes them interchangeable. This allows the algorithm to vary independently from clients that use it. The pattern promotes composition over inheritance by enabling the selection of an algorithm at runtime rather than at compile time.

In the original Gang of Four catalog, the Strategy pattern consists of three main participants:
- **Context**: Maintains a reference to a Strategy object and may define an interface that lets the Strategy access its data.
- **Strategy**: Declares an interface common to all supported algorithms.
- **ConcreteStrategy**: Implements the algorithm using the Strategy interface.

The key advantage of the Strategy pattern is that it decouples the implementation details of an algorithm from the code that uses it. This makes it straightforward to add new algorithms without modifying existing code, adhering to the Open/Closed Principle. Common use cases include sorting algorithms (where different sorting strategies can be swapped), compression algorithms, payment processing (credit card, PayPal, etc.), and validation rules.

In modern programming languages, the Strategy pattern can often be implemented more lightweightly using first-class functions, lambda expressions, or function objects. For example, in JavaScript or Python, instead of defining a hierarchy of ConcreteStrategy classes, you can pass a function directly to the Context. Similarly, in Java, functional interfaces and lambda expressions can replace explicit strategy class hierarchies. This reduces boilerplate code while still achieving the core separation of concerns.

The pattern is closely related to [[dependency-injection]] (often listed as dependency injection of function objects) and can be seen as a specific case of the [[observer-pattern]] in terms of decoupling, though their intents differ. The Strategy pattern focuses on interchangeable algorithms, while the Observer pattern addresses one-to-many notifications.

The term “strategy pattern” comes from the Gang of Four book *Design Patterns: Elements of Reusable Object-Oriented Software* (1994). Despite changes in programming paradigms, it remains a fundamental tool for building extensible, maintainable systems.

## See also
- [[design-patterns]]
- [[factory-pattern]]
- [[observer-pattern]]
- [[decorator-pattern]]
- [[dependency-injection]]
