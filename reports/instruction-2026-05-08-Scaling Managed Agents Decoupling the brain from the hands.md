# Convert Instruction: Scaling Managed Agents Decoupling the brain from the hands.md
> Generated: 2026-05-08

## Concepts Extracted

- **managed-agents** (create): Anthropic 推出的托管服务，通过将会话、控制循环和沙盒解耦，运行长期代理任务。
- **agent-decoupling-architecture** (merge → harness-engineering): 一种将代理的“大脑”（控制循环）与“手”（沙盒/工具）及状态日志解耦的架构模式，旨在提高系统的鲁棒性和可替换性。
- **session-log** (create): 持久化的仅追加日志，记录代理运行期间的所有事件，允许系统在崩溃后从断点恢复。
- **pets-vs-cattle** (create): 一种服务器管理隐喻，类比“宠物”为需要精心维护的独特实例，“牲畜”为可随时替换的标准化资源，文中主张将代理容器视为“牲畜”。
- **context-anxiety** (create): 指 AI 模型在感知上下文窗口即将耗尽时，倾向于过早完成任务或总结的行为。
- **sandbox-isolation** (create): 一种安全设计模式，将敏感凭证（如 Auth Token）存储在沙盒外部，通过代理或初始化注入使用，防止代码执行环境直接访问密钥。
- **context-window** (merge → large-language-model): 大语言模型单次处理所能参考的最大文本长度限制，长期任务需通过上下文工程（如摘要）来克服此限制。

## Ambiguities

- **managed-agents**: Managed Agents 是专有产品名称还是通用架构模式？
  Resolution: 将其定义为 Anthropic 的特定产品/服务页面，同时将其架构理念归纳到 'harness-engineering' 中。
- **harness**: 文中 Harness 指调用 Claude 的控制循环，而现有 Wiki 可能仅指 Codex 的相关工程；
  Resolution: 将新架构模式合并到 'harness-engineering'，但需注意该页面目前侧重 OpenAI/Codex，建议在摘要中体现定义的扩展。
