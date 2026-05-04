# codex-app-server

> Source(s): raw/Unlocking the Codex harness how we built the App Server.md

**Codex App Server** 是一个双向 JSON-RPC API，作为客户端和 Codex 核心代理循环（harness）之间的桥梁。它支持流式进度更新、工具使用、审批和差异展示，是嵌入 Codex 功能的关键接口。

## 背景与起源

Codex App Server 最初是为了在不同产品之间复用 Codex 核心代理循环而设计的实用方案，后来演变为 OpenAI 的标准协议。

- **Codex CLI** 以终端用户界面（TUI）形式运行，通过终端访问 Codex。
- **VS Code 扩展** 需要以 IDE 友好的方式驱动相同的代理循环，支持工作区探索、流式进度和差异输出等丰富交互模式。
- 最初尝试将 Codex 作为 MCP 服务器暴露，但维护 MCP 语义在 VS Code 中困难重重。最终引入了一个镜像 TUI 循环的 JSON-RPC 协议，这就是 **Codex App Server** 的非正式第一版。

随着 Codex 被 JetBrains、Xcode 等内部团队和外部合作伙伴集成，App Server 被设计为一个稳定、向后兼容的平台接口，使不同客户端可以安全地依赖同一个代理循环。

## Codex Harness 架构

Codex Harness 是驱动所有 Codex 体验的代理循环和逻辑。App Server 将其暴露给客户端的关键组件包括：

### 1. 线程生命周期与持久化
- **线程**是用户与代理之间的 Codex 会话。
- Codex 支持创建、恢复、分支和归档线程。
- 事件历史被持久化，客户端可以重新连接并渲染一致的时间线。

### 2. 配置与认证
- 加载配置，管理默认设置，运行“通过 ChatGPT 登录”等认证流程，包括凭据状态。

### 3. 工具执行与扩展
- 在沙箱中执行 shell/文件工具。
- 连接 MCP 服务器和技能等集成，使其在一致的政策模型下参与代理循环。

## App Server 内部结构

App Server 既是客户端与服务器之间的 JSON-RPC 协议，也是一个长期运行的进程，负责托管 Codex 核心线程。其四个主要组件为：

1. **stdio reader**：读取标准输入。
2. **Codex message processor**：处理消息，作为客户端与核心线程之间的翻译层。
3. **thread manager**：为每个线程启动一个核心会话。
4. **core threads**：实际的 Codex 核心会话。

客户端的一个请求可能产生多个事件更新，这些细粒度事件使得在 App Server 之上构建丰富的 UI 成为可能。

### 翻译层的工作流程
- stdio reader 和 Codex message processor 将客户端 JSON-RPC 请求转换为 Codex 核心操作。
- 监听 Codex 核心的内部事件流。
- 将底层事件转换为一小组稳定的、面向 UI 的事件，供客户端消费。

## 关键特性

- **双向通信**：支持流式进度、工具使用、审批和差异展示。
- **客户端无关性**：同一个 App Server 可以服务于终端、IDE 扩展、桌面应用等不同前端。
- **向后兼容**：协议设计允许演进而不破坏现有客户端。
- **线程管理**：支持多线程并发，适用于需要编排多个 Codex 代理的场景（如 Codex 桌面应用）。

## 使用场景

App Server 使得将 Codex 嵌入到不同产品中成为可能，典型应用包括：

- **代码审查代理**：将 Codex 转换为自动代码审查工具。
- **SRE 代理**：用于系统运维和故障排查。
- **编程助手**：集成到 IDE 或终端中的日常编码辅助。

## 参见

- [[harness-engineering]]
- [[agents-dot-md]]
- [[agent-first-world]]
- [[codex-cli]]
- [[ralph-wiggum-loop]]
- [[gpt-series]]