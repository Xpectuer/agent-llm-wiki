---
brief: 事件溯源将状态变更存储为不可变事件序列，提供完整审计与时间查询能力，常与CQRS配合实现。
---

# Event Sourcing

> Source(s): raw/ch-03-Continuous Integration and Delivery

Event sourcing is an architectural pattern where state changes in a system are persisted as a sequence of immutable events, rather than storing the current state as a snapshot. Instead of updating a database record in place, each business operation that changes state produces an event that is appended to an event store. The current state of any entity can be reconstructed by replaying all events in order from the beginning.

This approach provides a complete audit trail—every change is recorded, including who made it and when. It also enables **temporal queries**: you can determine the state of the system at any point in the past by replaying events up to that time. Event sourcing is often paired with **Command Query Responsibility Segregation (CQRS)** to separate write-side event generation from read-side projections that materialize views for queries.

## Relationship with Event-Driven Architectures

The **Observer pattern**, discussed in the source material, “defines a one-to-many dependency between objects: when one object changes state, all its dependents are notified automatically.” Event sourcing extends this idea to persistence—events are not only notifications but also the source of truth. In modern systems, “message brokers like RabbitMQ and Kafka implement publish-subscribe at scale,” and event sourcing can be built on top of such brokers by treating the event stream as the primary data store. Kafka, for instance, is a popular choice for an event store due to its append-only log, immutability, and replay capabilities.

## Benefits and Challenges

**Advantages:**
- **Complete audit trail:** Every state change is recorded, satisfying compliance and debugging needs.
- **Temporal reasoning:** Replay events to reconstruct past states or debug historical bugs.
- **Decoupled evolution:** Read-side projections can be added or changed without affecting the write side.
- **Testability:** Replaying events in tests provides deterministic state reconstruction.

**Challenges:**
- **Event schema evolution:** As the system evolves, old events may have incompatible formats; versioning strategies (e.g., upcasting, event transformation) are required.
- **Storage overhead:** Instead of a single row, many events accumulate over time; snapshotting (periodically storing a state projection) is often used to bound reconstruction costs.
- **Consistency complexity:** Eventual consistency between the event store and projections must be managed carefully, especially when CQRS is used.

## When to Use Event Sourcing

Event sourcing is most valuable in domains where audit, history, or complex state reconstruction are first-class requirements—such as financial systems, compliance-heavy workflows, multiplayer games (player actions as events), and collaborative editing systems. It is overkill for simple CRUD applications where the cost of event management outweighs the benefits.

## See also
- [[cqrs]]
- [[observer-pattern]]
- [[repository-pattern]]
- [[system-architecture]]
- [[testing-pyramid]]
