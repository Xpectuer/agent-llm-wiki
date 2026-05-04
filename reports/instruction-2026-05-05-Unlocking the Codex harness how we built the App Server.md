# Convert Instruction: Unlocking the Codex harness how we built the App Server.md
> Generated: 2026-05-05

## Concepts Extracted

- **codex-app-server** (create): Codex App Server是一个双向JSON-RPC API，作为客户端和Codex核心代理循环之间的桥梁，支持流式进度、工具使用、审批和差异展示，是嵌入Codex功能的关键接口。
- **json-rpc-protocol** (create): Codex App Server使用的双向JSON-RPC协议，客户端请求可触发多个服务器通知，服务器也可发起请求（如审批），支持丰富交互模式。
- **codex-harness** (merge → harness-engineering): Codex harness是支撑所有Codex体验的代理循环和逻辑层，包含核心代理循环、线程生命周期和持久化、配置和认证、工具执行和扩展。
- **thread-lifecycle** (create): 线程是Codex中用户与代理之间的对话容器，支持创建、恢复、分叉和归档操作，并持久化事件历史以供客户端重新连接和渲染一致时间线。
- **conversation-primitives** (create): Codex App Server协议的核心构建块：Item是输入/输出的原子单元，有明确生命周期；Turn是用户输入引发的一组代理工作单元；Thread是持久化会话容器。
- **agent-loop-items-turns-threads** (merge → codex-cli): Codex交互模式通过Item（原子单元）、Turn（代理工作单元）和Thread（会话容器）三个层次组织，支持流式更新和精确状态管理。
- **codex-core** (create): Codex core是位于Codex CLI代码库中的库和运行时，包含所有代理逻辑（核心代理循环、线程持久化等），可独立运行管理单个Codex线程。

## Ambiguities

- **codex-harness**: 现有页面 'harness-engineering' 定义的是方法论（通过设计环境指导代理），而 'codex-harness' 是具体的技术实现（Codex的代理循环和逻辑层）。二者存在概念重叠但层次不同。
  Resolution: 将 'codex-harness' 作为具体实现案例合并到 'harness-engineering' 页面，在 'harness-engineering' 中增加“实例：Codex harness”子章节详细描述技术细节。
- **conversation-primitives / agent-loop-items-turns-threads**: 'conversation-primitives' 和 'agent-loop-items-turns-threads' 描述的是同一组对象（Item、Turn、Thread），但前者强调协议设计，后者强调交互模式。存在概念重复。
  Resolution: 合并为一个概念，建议统一命名为 'codex-conversation-primitives'，同时覆盖协议层面和交互层面的描述。此处保留 'conversation-primitives' 作为新建页面，将 'agent-loop-items-turns-threads' 合并到 'codex-cli' 页面作为补充说明。
- **codex-core**: 现有页面 'codex-cli' 已包含Codex CLI的整体描述，但未明确区分核心逻辑库（codex core）与CLI界面层。'codex-core' 是更底层的组件，可能与 'harness-engineering' 中的实现部分混淆。
  Resolution: 推荐新建 'codex-core' 页面，明确其作为独立库/运行时的定位，并在 'codex-cli' 页面中增加指向 'codex-core' 的引用，说明CLI依赖core组件。
