# conversation-primitives

> Source(s): raw/Unlocking the Codex harness how we built the App Server.md

conversation-primitives 是 Codex App Server 协议中定义对话交互的三个核心构建块：Item、Turn 和 Thread。这些原语共同构成了 Codex 代理系统与用户交互的基础架构，支持持久化会话、流式响应和工具执行等复杂交互模式。

## 核心概念

**Item (项)** 是输入/输出的原子单元，具有明确的创建、提交和关闭生命周期。每个 Item 代表一次单一的用户消息或代理生成的响应片段，例如代码片段、文本块或工具执行结果。

**Turn (回合)** 是由用户输入触发的一组代理工作单元。一次用户请求触发一个 Turn，Turn 内包含代理推理、工具调用、文件修改等所有相关操作，直到向用户返回最终响应。Turn 是理解用户请求完整处理过程的逻辑边界。

**Thread (线程)** 是持久化的会话容器，包含整个对话历史。Thread 支持完整的生命周期管理——创建、继续、分支和归档——并将事件历史持久化，使客户端能够重新连接并呈现一致的时间线。Codex 核心运行时会为每个 Thread 维护一个独立的会话。

## 架构设计

Codex App Server 同时扮演两个角色：
1. **JSON-RPC 协议**：客户端与服务器之间的双向通信接口
2. **长期运行的服务进程**：托管 Codex 核心线程

App Server 进程包含四个主要组件：
- **stdio reader**：读取客户端请求
- **Codex message processor**：处理并转发消息
- **thread manager**：管理多个核心会话，为每个 Thread 启动一个核心会话
- **core threads**：实际的 Codex 代理会话

客户端的一次请求可以产生多个事件更新，这些细粒度的事件使得在 App Server 之上构建丰富的用户界面成为可能。stdio reader 和 Codex message processor 作为客户端与核心线程之间的翻译层，将客户端 JSON-RPC 请求转换为核心操作，监听核心的内部事件流，并将底层事件转换为一组稳定的、对 UI 友好的高层事件。

## 设计动机与演变

conversation-primitives 的演化源于实际产品需求。最初，Codex CLI 是一个终端用户界面（TUI），当需要构建 VS Code 扩展时，团队发现需要在不重新实现代理逻辑的情况下复用相同的 Codex 核心运行时。这需要支持超越简单请求/响应模式的丰富交互，例如工作区浏览、代理推理过程流式传输以及差异对比（diff）输出。

团队最初尝试将 Codex 暴露为 MCP 服务器，但维持语义一致性变得困难。随后引入的 JSON-RPC 协议镜像了 TUI 循环，成为 App Server 的第一个非官方版本。随着 Codex 被更多产品采用（JetBrains、Xcode、Codex 桌面应用等），这些原语被设计为稳定、向后兼容的平台 API，使得不同客户端能够安全依赖并逐步演进。

## 在完整代理体验中的角色

conversation-primitives 是完整 Codex 代理体验的基石，覆盖以下关键系统：

1. **Thread 生命周期与持久化**：创建、恢复、分支和归档对话，持久化事件历史以便客户端重连和渲染
2. **配置与认证**：加载配置、管理默认值、执行认证流程（如"通过 ChatGPT 登录"）
3. **工具执行与扩展**：在沙箱中执行 shell/文件工具，集成 MCP 服务器和技能，在统一策略模型下参与代理循环

所有代理逻辑（包括核心代理循环）位于 Codex CLI 代码库的 "Codex core" 部分。Codex core 既是包含所有代理代码的库，也是可启动以运行代理循环并管理单个 Thread 持久化的运行时。

## See also
- [[codex-app-server]]
- [[json-rpc-protocol]]
- [[thread-lifecycle]]
- [[gpt-series]]
