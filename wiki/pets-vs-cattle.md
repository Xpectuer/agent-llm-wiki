# Pets vs. Cattle

> Source(s): raw/Scaling Managed Agents Decoupling the brain from the hands.md

**Pets vs. Cattle** is a metaphor used in server management and infrastructure engineering to describe two different approaches to handling computing resources.

*   **Pets**: Servers (or containers) that are treated as unique, named individuals. They are carefully maintained, hand-tended, and nursed back to health if they become sick. You cannot afford to lose them.
*   **Cattle**: Servers that are treated as interchangeable, standardized resources. If one becomes sick or fails, it is simply replaced by another using a standard provisioning recipe. They are numbered rather than named.

In the context of agent architecture, applying the "cattle" philosophy means designing systems where components (such as sandboxes or agent harnesses) are stateless and disposable, allowing for resilience and easier scaling.

## Application in Managed Agents

The "pets vs. cattle" analogy is central to the architectural decisions behind scaling managed agents effectively. The goal is to avoid the pitfalls of treating infrastructure as unique "pets" that require constant maintenance.

### The Problem with Pets

Initially, agent components (the session, harness, and sandbox) were bundled into a single container. While this simplified file edits and removed service boundaries, it created a significant infrastructure risk: **the container became a "pet."**

Because the session state was tightly coupled with the container, the system could not afford to lose it. If a container failed, the session was lost. If a container became unresponsive, engineers were forced to "nurse" it back to health.

This introduced specific operational difficulties:
*   **Debugging Opacity**: The only insight into a stuck session was a WebSocket event stream, which did not reveal the root cause of failures (e.g., a harness bug vs. a packet drop).
*   **Security Risks**: Debugging required opening a shell inside the container, which was often prohibited due to the presence of user data.
*   **Rigidity**: The harness assumed the workspace lived inside the container. Connecting agents to external customer infrastructure (like a Virtual Private Cloud) required complex network peering or invasive deployment of the harness into customer environments.

### The Solution: Cattle

To scale managed agents reliably, the architecture was shifted to treat components as "cattle." This involved **decoupling the "brain" (Claude and the harness) from the "hands" (sandboxes) and the "session" (the event log).**

*   **Sandboxes as Cattle**: The harness now treats the sandbox/container as just another tool to be called via `execute(name, input)`.
    *   If a container (the "hands") dies, the harness catches the error as a standard tool failure.
    *   Claude can simply retry, and a new container is provisioned using a standard `provision({resources})` recipe.
    *   There is no need to nurse failed containers; they are immediately replaced.
*   **Harnesses as Cattle**: The harness itself is designed to be disposable.
    *   Because the **Session** (the append-only log of events) is stored externally, the harness does not need to maintain state.
    *   If the harness crashes, a new one is rebooted with a `wake(sessionId)` command. It retrieves the event log via `getSession(id)` and resumes execution from the last event.

By treating infrastructure as "cattle," the system gains resilience, simplifies debugging, and removes the tight coupling between the agent logic and the execution environment.

## See also
- [[sandbox-isolation]]
- [[managed-agents]]
- [[session-log]]
*   [[json-rpc-protocol]]
