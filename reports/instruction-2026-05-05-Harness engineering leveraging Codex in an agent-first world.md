# Convert Instruction: Harness engineering leveraging Codex in an agent-first world.md
> Generated: 2026-05-05

## Concepts Extracted

- **harness-engineering** (create): 一种软件工程方法论，强调通过设计环境、指定意图和构建反馈循环，让AI代理（如Codex）负责代码编写，人类工程师专注于系统设计和策略引导。
- **agent-first-world** (create): 一种以AI代理为执行主体的软件开发范式，人类角色从编码者转变为设计者和监督者。
- **codex-cli** (create): OpenAI Codex的命令行界面工具，允许代理使用GPT-5等模型直接生成和操作代码。
- **human-steer-and-agent-execute** (merge → harness-engineering): 核心理念：人类负责总体方向、设计和反馈，AI代理负责具体的代码执行和实现。
- **ralph-wiggum-loop** (create): 一种代码审查循环策略，代理在本地和云端自行审查代码，迭代直到满足所有审查条件，无需人类介入。
- **agents-dot-md** (create): 一种以 `AGENTS.md` 文件作为知识目录、指向更详细文档（如 `docs/`）的代理工作引导策略。
- **codex** (merge → gpt-series): OpenAI开发的代码生成模型，在本文中被用作零手工编码工程的代执行引擎。

## Ambiguities

- **harness-engineering**: “Harness engineering” 在本文中特指一种以Codex代理为中心的工程实践，可能与其它上下文中用于描述测试或DevOps工具的“harness”概念混淆。
  Resolution: 建议新建页面，明确其含义为“通过代理引导代码生成与工程管理的工程范式”。
- **codex**: “Codex” 在本文中既指代OpenAI的代码生成模型作为“执行代理”，也指代具体的CLI工具（Codex CLI）。摘要中应区分模型与工具，建议在 `codex` 页面中明确包含这两者角色。
  Resolution: 在对应的合并页面（如 `gpt-series`）和新建页面（如 `codex-cli`）中明确说明两者的关系。
- **agents-dot-md**: “AGENTS.md” 策略与传统的“单一大手册”记录方式冲突，容易与其它仓库通用文档区分。
  Resolution: 作为独立概念创建，并说明其作为“知识目录”而非“知识全集”的独特设计。
