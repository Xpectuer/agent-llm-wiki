```markdown
# session-log

> Source(s): Scaling Managed Agents Decoupling the brain from the hands.md

A **session-log** is a persistent, append-only log that records all events occurring during an agent's runtime. It serves as the canonical source of truth for a session's history, enabling the system to recover from a crash and resume execution from the exact point of failure.

In the architecture of managed agents, the session log is a critical abstraction that allows the system to treat both the "brain" (the agent harness) and the "hands" (sandboxes and tools) as ephemeral resources—often referred to as "cattle" rather than "pets"—because the state is preserved externally in the log.

## Key Characteristics

*   **Append-only:** New events are strictly added to the end of the log; history is never mutated.
*   **Persistent:** The log exists outside of the container or process running the agent logic, ensuring it survives crashes.
*   **Indivisible State:** It represents the complete context required to reconstruct or continue a session.

## Architecture and Decoupling

The session log is fundamental to the decoupling of the agent components. By moving the session log out of the harness and container, the system gains significant resilience:

1.  **Harness as "Cattle":** Because the session log is external, the harness itself does not need to maintain state to survive a failure. If a harness crashes, a new instance can be booted and retrieve the session history via `getSession(id)`, allowing it to `wake(sessionId)` and resume from the last event.
2.  **Recovery Mechanism:** The log allows the system to handle "brain" failures (logic errors in the harness) and "hand" failures (container crashes) uniformly. The system simply replays or reads the log to the last checkpoint to understand the current state.
3.  **Debuggability:** Unlike systems where state is trapped inside a "pet" container (a server that must be nursed back to health), an external log provides a clear window into the sequence of events, making it easier to diagnose failures without accessing the internal state of a potentially dead container.

## See also
- [[managed-agents]]
- [[thread-lifecycle]]
- [[pets-vs-cattle]]
```
