# codex-core

> Source(s): raw/Unlocking the Codex harness how we built the App Server.md

**Codex core** is the library and runtime located within the [Codex CLI](https://github.com/openai/codex) codebase that contains all agent logic, including the core agent loop, thread persistence, configuration management, and tool execution. It can be run independently to manage a single Codex thread (conversation).

## Overview

Codex core is the fundamental engine that powers all Codex experiences across different surfaces—the web app, CLI, IDE extension, and macOS app. It encapsulates the core agent loop that orchestrates the interaction between the user, the model, and the tools. All the agent logic, including thread lifecycle management, configuration and authentication, and tool execution, resides in the `codex-rs/core` directory of the Codex CLI repository.

## Core Components

### 1. Thread Lifecycle and Persistence

Codex core manages the full lifecycle of Codex threads (conversations between a user and an agent). It handles creating, resuming, forking, and archiving threads, and persists event history so that clients can reconnect and render a consistent timeline.

### 2. Configuration and Authentication

The core loads configuration, manages defaults, and runs authentication flows (e.g., "Sign in with ChatGPT"), including credential state management.

### 3. Tool Execution and Extensions

Codex core executes shell and file tools in a sandbox environment. It also wires up integrations like Model Context Protocol (MCP) servers and skills, enabling them to participate in the agent loop under a consistent policy model.

## Relationship with the Codex App Server

The Codex App Server exposes the capabilities of Codex core to client applications via a bidirectional JSON-RPC API. The App Server hosts Codex core threads, allowing multiple clients to leverage the same harness without re-implementing the agent logic. The translation layer (stdio reader and Codex message processor) converts client JSON-RPC requests into Codex core operations and transforms low-level events into stable, UI-friendly event streams.

## Applications

Codex core's architecture enables diverse use cases:
- **Code Reviewers**: Embed the agent loop for automated code analysis
- **SRE Agents**: Use the harness for system administration tasks
- **Coding Assistants**: Integrate the agent as a general-purpose programming helper

The core was originally developed as part of the Codex CLI and was later extracted to support IDE extensions (like VS Code, JetBrains, Xcode) and the Codex desktop app, which required orchestrating multiple agents in parallel.

## See also
- [[codex-app-server]]
- [[thread-lifecycle]]
- [[harness-engineering]]
- [[gpt-series]]
