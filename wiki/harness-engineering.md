# Harness Engineering

> Source(s): raw/Harness engineering leveraging Codex in an agent-first world.md, raw/Unlocking the Codex harness how we built the App Server.md

**Harness engineering** is a software engineering methodology that emphasizes designing environments, specifying intent, and building feedback loops to let AI agents (such as Codex) handle code writing, while human engineers focus on system design and strategic guidance. The term was coined by the OpenAI team in a 2025 experiment where a software product was built and shipped with **zero lines of manually-written code**.

At the core of harness engineering lies the **Codex harness**—the agent loop and logic layer that powers all Codex experiences. The Codex harness includes the core agent loop, thread lifecycle and persistence, configuration and authentication, and tool execution and extensions. The critical link between the harness and various client surfaces (web app, CLI, IDE extension, macOS app) is the **Codex App Server**, a client-friendly, bidirectional JSON-RPC API that enables streaming progress, tool use, approvals, and diffs.

## Overview

Harness engineering represents a fundamental shift in the role of software engineers. Instead of writing code directly, engineers act as system architects and guides, creating the conditions under which AI agents can produce reliable, high-quality software. The core philosophy is: **humans steer, agents execute**.

The methodology was developed during a five-month experiment at OpenAI (beginning August 2025) where a small team built a product with approximately one million lines of code—across application logic, tests, CI configuration, documentation, observability, and internal tooling—entirely through Codex-generated code. The team estimated this was accomplished in about 1/10th the time it would have taken to write the code by hand.

The product has internal daily users and external alpha testers. It ships, deploys, breaks, and gets fixed. The experiment was documented by Ryan Lopopolo, Member of the Technical Staff at OpenAI, in an April 2026 blog post, with further architectural details shared in subsequent posts by Celia Chen and other team members.

## Inside the Codex Harness

The Codex harness is composed of several key components that work together to deliver the full agent experience:

### 1. Core Agent Loop
The core agent loop orchestrates the interaction between the user, the model, and the tools. This is the central logic that drives decision-making, reasoning, and action execution in Codex agents.

### 2. Thread Lifecycle and Persistence
A thread is a Codex conversation between a user and an agent. Codex creates, resumes, forks, and archives threads, and persists the event history so clients can reconnect and render a consistent timeline. This ensures continuity across sessions and devices.

### 3. Configuration and Authentication
Codex loads configuration, manages defaults, and runs authentication flows such as "Sign in with ChatGPT," including credential state management. This layer handles user preferences, API keys, and access control.

### 4. Tool Execution and Extensions
Codex executes shell and file tools in a sandboxed environment and wires up integrations like MCP servers and skills so they can participate in the agent loop under a consistent policy model. This extensibility allows third-party tools and custom capabilities to be added seamlessly.

All agent logic, including the core agent loop, resides in a part of the Codex CLI codebase called "Codex core"—a library and runtime that can be spun up to run the agent loop and manage the persistence of one Codex thread.

## The Codex App Server

The Codex App Server is both the JSON-RPC protocol between the client and the server and a long-lived process that hosts the Codex core threads. An App Server process has four main components:

- **The stdio reader**: Handles input/output communication
- **The Codex message processor**: Translates client JSON-RPC requests into Codex core operations, and transforms low-level events into stable UI-friendly updates
- **The thread manager**: Spins up one core session for each thread
- **Core threads**: Individual sessions running the agent loop

One client request can result in many event updates, enabling rich UI development. The translation layer between client and Codex core threads ensures backward compatibility and allows the protocol to evolve without breaking existing clients.

### Origin of the App Server

The Codex App Server originated as a practical solution to reuse the Codex harness across different products. Codex CLI started as a terminal user interface (TUI). When the team built the VS Code extension, they needed a way to use the same harness for driving the same agent loop from an IDE UI—supporting rich interaction patterns like workspace exploration, streaming progress, and diff emission.

Initially, the team experimented with exposing Codex as an MCP server, but maintaining MCP semantics for VS Code proved difficult. Instead, they introduced a JSON-RPC protocol that mirrored the TUI loop, which became the unofficial first version of the App Server. As adoption grew—with internal teams and external partners like JetBrains and Xcode wanting to embed the same harness—the App Server evolved into a platform surface designed for stability, ease of integration, and backward compatibility.

## Key Principles

1. **No manually-written code**: Human engineers never directly contribute code. Every line is produced by AI agents. This became a core philosophy for the team.

2. **Environment-first design**: Progress is enabled not by "trying harder" with agents, but by identifying missing capabilities and making them legible and enforceable for the agent. When something failed, the fix was almost never "try harder"—instead, engineers asked "what capability is missing, and how do we make it both legible and enforceable for the agent?"

3. **Depth-first decomposition**: Break larger goals into smaller building blocks (design, code, review, test), prompt the agent to construct those blocks, and use them to unlock more complex tasks. This depth-first approach was essential for overcoming early progress bottlenecks.

4. **Agent-to-agent review loops**: Codex reviews its own changes locally, requests additional agent reviews, responds to feedback, and iterates until all agent reviewers are satisfied (a pattern called the *Ralph Wiggum Loop*). Over time, nearly all review effort has been pushed towards being handled agent-to-agent.

5. **Application legibility**: Make the application UI, logs, and metrics directly legible to Codex so agents can reproduce bugs, validate fixes, and reason about system behavior.

## Implementation Approaches

### Starting from Scratch

In the original experiment, the repository began empty. The initial scaffold—repository structure, CI configuration, formatting rules, package manager setup, and application framework—was generated by Codex CLI using GPT‑5, guided by a small set of existing templates. Even the initial AGENTS.md file that directs agents was written by Codex. There was no pre-existing human-written code to anchor the system; from the beginning, the repository was shaped by the agent.

### Architecture for Agent Access

Key implementation patterns include:
- Making the app bootable per git worktree, allowing Codex to launch and drive one instance per change
- Wiring the Chrome DevTools Protocol into the agent runtime for working with DOM snapshots, screenshots, and navigation
- Exposing logs, metrics, and traces via an ephemeral local observability stack that gets torn down per task
- Using standard development tools (gh, local scripts, and repository-embedded skills) for context gathering without humans copying and pasting into the CLI

### Feedback Loop Design

Agents can query logs with LogQL and metrics with PromQL. This enables prompts like "ensure service startup completes in under 800ms" or "no span in these four critical user journeys exceeds two seconds." The feedback loops allow agents to self-correct and iterate on tasks reliably. With this context available, Codex works on fully isolated versions of the app—including its logs and metrics, which get torn down once that task is complete.

## Results

- **Throughput**: Approximately 1,500 pull requests merged over five months with a team of 3-7 engineers
- **Velocity**: Average of 3.5 PRs per engineer per day, with throughput *increasing* as the team grew to seven engineers
- **Scale**: Product with millions of lines of code serving hundreds of internal users and external alpha testers, including daily internal power users
- **Time savings**: Estimated 10x reduction in development time compared to manual coding
- **Output quality**: This was not output for output's sake; the product has been actively used throughout development

## Human Role in Harness Engineering

The lack of hands-on coding introduces a different kind of engineering work, focused on:
- Systems design and scaffolding
- Creating leverage for agents
- Identifying missing capabilities and making them legible to agents
- Specifying intent through prompts (humans interact with the system almost entirely through prompts)
- Designing and maintaining feedback loops
- Strategic guidance and quality assurance (as a secondary concern, since most review becomes agent-to-agent)
- Driving pull requests to completion by instructing Codex to self-review, request agent reviews, respond to feedback, and iterate until all agent reviewers are satisfied

Humans may review pull requests, but aren't required to. The primary job of engineers is to enable agents to do useful work, maximizing the one truly scarce resource: human time and attention.

## See also
- [[agent-first-world]]
- [[codex-cli]]
- [[codex-app-server]]
- [[ralph-wiggum-loop]]
- [[json-rpc-protocol]]