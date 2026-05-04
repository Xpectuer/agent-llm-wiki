# JSON-RPC Protocol

> Source(s): raw/Unlocking the Codex harness how we built the App Server.md

The **JSON-RPC Protocol** is the bidirectional communication protocol used by the Codex App Server, enabling rich interaction between client applications and the Codex agent harness. Unlike traditional request-response APIs, this protocol supports streaming progress, tool execution updates, approval workflows, and server-initiated requests, making it ideal for embedding AI coding agents in various surfaces.

## Overview

The JSON-RPC Protocol serves as the critical link between the Codex harness (the core agent loop and logic) and client applications. It was originally developed as a practical way to reuse the Codex harness across different products, evolving from a terminal user interface (TUI) into a standard protocol that both OpenAI products and partner integrations can safely depend on.

The protocol was born from the need to support rich interaction patterns beyond simple request/response, such as:
- Exploring the workspace
- Streaming progress as the agent reasons
- Emitting diffs
- Server-initiated requests (e.g., approvals)

Initial experiments used MCP (Model Context Protocol) semantics, but maintaining them for VS Code proved difficult. The team instead introduced a JSON-RPC protocol that mirrored the TUI loop, which became the unofficial first version of the App Server.

## Architecture

The App Server process has four main components:

1. **stdio reader** – Reads JSON-RPC requests from standard input
2. **Codex message processor** – Translates client JSON-RPC requests into Codex core operations
3. **Thread manager** – Spins up one core session for each thread
4. **Core threads** – Execute the agent loop for each conversation

The stdio reader and Codex message processor serve as a translation layer between the client and Codex core threads. They:
- Translate client JSON-RPC requests into Codex core operations
- Listen to Codex core's internal event stream
- Transform low-level events into stable, UI-friendly event updates

## Key Features

### Bidirectional Communication
One client request can result in many event updates, enabling rich UI rendering. The server can also initiate requests to the client, such as approval dialogs.

### Event Streaming
Detailed events allow building rich user interfaces on top of the App Server, including progress indicators, tool execution results, and incremental updates.

### Backward Compatibility
The protocol is designed to evolve without breaking existing clients, ensuring long-term stability for integrations.

## Use Cases

The protocol enables diverse integration scenarios:

- **IDE Integration**: VS Code extension, JetBrains, Xcode
- **Desktop Application**: Codex macOS app orchestrating multiple agents in parallel
- **Code Reviewer**: Embedding Codex as an automated code review assistant
- **SRE Agent**: Using Codex for infrastructure and operations tasks
- **Coding Assistant**: General-purpose AI-powered development help

## Relationship to Codex Harness

The JSON-RPC Protocol exposes the Codex harness to client applications. The harness includes:

1. **Thread lifecycle and persistence** – Creating, resuming, forking, and archiving conversations
2. **Config and auth** – Loading configuration, managing defaults, authentication flows
3. **Tool execution and extensions** – Running shell/file tools in sandboxes, integrating MCP servers and skills

All agent logic lives in "Codex core," a library and runtime that can spin up to run the agent loop and manage thread persistence.

## See also

- [[harness-engineering]]
- [[codex-cli]]
- [[agents-dot-md]]
- [[ralph-wiggum-loop]]