```markdown
# Sandbox Isolation

> Source(s): raw/Scaling Managed Agents Decoupling the brain from the hands.md

**Sandbox Isolation** (in the context of Managed Agents architecture) is a security design pattern where the execution environment (the "hands") is decoupled from the control logic (the "brain").

Instead of running agent components—such as the session log, the harness, and the sandbox—within a single shared container, this pattern enforces strict separation. Specifically, the harness (controller) operates **outside** the sandbox environment.

## Architecture & Implementation

In the decoupled architecture described in the evolution of Managed Agents, the sandbox is treated as an ephemeral resource or a tool that can be provisioned and destroyed on demand.

### Interaction Model
The harness interacts with the sandbox environment using a generic execution interface:
`execute(name, input) → string`

This abstraction treats the sandbox container as "cattle" (interchangeable resources) rather than "pets" (unique, persistent servers). This allows the system to handle failures gracefully:
1.  **Resilience**: If a sandbox container fails or dies, the harness catches the failure as a standard tool-call error.
2.  **Recovery**: The system can provision a new container using a standard recipe (`provision({resources})`) without losing the state of the overall session.

### Security & Access Control
By decoupling the harness from the execution environment, the system avoids the risks associated with "adoption" (where components are tightly coupled in one environment).
*   **Network Boundaries**: The harness is not bound to the network of the container. This allows agents to interact with external infrastructures, such as a customer's Virtual Private Cloud (VPC), without requiring network peering or running the harness inside the customer's environment.
*   **State Separation**: Because the session log and the harness logic reside outside the sandbox, the failure of a sandbox container does not result in the loss of the agent's "brain" or history.

## See also
- [[pets-vs-cattle]]
- [[managed-agents]]
- [[harness-engineering]]
```
