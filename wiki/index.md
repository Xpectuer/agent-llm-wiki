# Wiki Index

> Last updated: 2026-05-08

## Concepts
<!-- Add conceptual wiki pages here -->

## Entities
<!-- Add entity pages here -->

## Sources
<!-- Add source reference pages here -->

## Synthesis
- [[context-window]] -- 大语言模型单次处理所能参考的最大文本长度限制，长期任务需通过上下文工程（如摘要）来克服此限制。
- [[sandbox-isolation]] -- 一种安全设计模式，将敏感凭证（如 Auth Token）存储在沙盒外部，通过代理或初始化注入使用，防止代码执行环境直接访问密钥。
- [[context-anxiety]] -- 指 AI 模型在感知上下文窗口即将耗尽时，倾向于过早完成任务或总结的行为。
- [[pets-vs-cattle]] -- 一种服务器管理隐喻，类比“宠物”为需要精心维护的独特实例，“牲畜”为可随时替换的标准化资源，文中主张将代理容器视为“牲畜”。
- [[session-log]] -- 持久化的仅追加日志，记录代理运行期间的所有事件，允许系统在崩溃后从断点恢复。
- [[agent-decoupling-architecture]] -- 一种将代理的“大脑”（控制循环）与“手”（沙盒/工具）及状态日志解耦的架构模式，旨在提高系统的鲁棒性和可替换性。
- [[managed-agents]] -- Anthropic 推出的托管服务，通过将会话、控制循环和沙盒解耦，运行长期代理任务。
- [[codex]] -- OpenAI开发的代码生成模型，在本文中被用作零手工编码工程的代执行引擎。
- [[agents-dot-md]] -- 一种以 `AGENTS.md` 文件作为知识目录、指向更详细文档（如 `docs/`）的代理工作引导策略。
- [[ralph-wiggum-loop]] -- 一种代码审查循环策略，代理在本地和云端自行审查代码，迭代直到满足所有审查条件，无需人类介入。
- [[human-steer-and-agent-execute]] -- 核心理念：人类负责总体方向、设计和反馈，AI代理负责具体的代码执行和实现。
- [[codex-cli]] -- OpenAI Codex的命令行界面工具，允许代理使用GPT-5等模型直接生成和操作代码。
- [[agent-first-world]] -- 一种以AI代理为执行主体的软件开发范式，人类角色从编码者转变为设计者和监督者。
- [[harness-engineering]] -- 一种软件工程方法论，强调通过设计环境、指定意图和构建反馈循环，让AI代理（如Codex）负责代码编写，人类工程师专注于系统设计和策略引导。
- [[large-language-model]] -- 具有海量参数的语言模型，在规模达到一定程度时会展现出解决复杂任务的涌现能力。
- [[self-attention-mechanism]] -- 一种完全依赖自身序列计算元素间关联权重的机制，是Transformer架构的核心。
- [[gpt-series]] -- 由OpenAI开发的基于Transformer解码器的生成式预训练语言模型系列，展现出强大的零样本学习和涌现能力。
- [[bert]] -- 基于Transformer编码器的预训练语言模型，通过掩码语言模型和下一句预测任务进行训练。
- [[transformer]] -- 一种基于自注意力机制的深度学习架构，摒弃了传统RNN和CNN结构，用于捕捉序列依赖关系。
<!-- Add synthesized/comparison pages here -->
