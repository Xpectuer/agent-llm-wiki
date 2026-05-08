# thread-lifecycle

> Source(s): raw/Unlocking the Codex harness how we built the App Server.md

线程是 Codex 中连接用户与代理的对话容器。它支持创建、恢复、分叉和归档操作，并持久化事件历史，使得客户端可以重新连接并渲染一致的时间线。

## 核心功能

- **创建线程**：启动一个新的对话上下文，用户与代理之间的交互从此开始。
- **恢复线程**：允许用户回到之前保存的会话，继续完成未完成的任务。
- **分叉线程**：从现有线程的某个点创建分支，用于探索不同的路径或实验新方案而不影响原线程。
- **归档线程**：将已完成或不再需要的线程保存起来，清理工作空间但保留历史记录以供将来参考。

## 持久化机制

线程的持久化功能确保所有事件历史（如用户输入、代理响应、工具调用结果等）被可靠存储。这使得客户端可以在任何时间点断开并重新连接，依然能获取完整的对话上下文和一致的事件时间线。

## 线程管理器

在 App Server 中，线程管理器（thread manager）负责管理所有活跃的线程。它为每个线程启动一个核心会话（core session），并通过 Codex 消息处理器与每个核心会话直接通信，以提交客户端请求并接收更新。

## 相关概念

- Codex 的核心引擎和代理循环参见 [[harness-engineering]]
- 线程运行在Codex代理上下文中，了解更多关于代理的基础知识参见 [[agents-dot-md]]
- 线程生命周期支持分叉和归档，这些操作与 [[agent-first-world]] 中的高阶工作流概念一致

## See also
- [[codex-app-server]]
- [[conversation-primitives]]
- [[session-log]]
- [[gpt-series]]