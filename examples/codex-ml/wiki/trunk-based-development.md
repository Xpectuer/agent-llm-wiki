---
brief: 主干开发是一种短生命周期分支策略，开发者频繁合并到主分支，配合功能开关使代码库始终处于可发布状态
---

# trunk-based-development

> Source(s): raw/ch-03-Continuous Integration and Delivery

Trunk-Based Development（主干开发）是一种与持续集成（CI）紧密配合的分支策略。其核心理念是：开发者工作在短生命周期的分支上（理想情况下短于一天），并频繁地将代码合并到主分支（主干）。通过功能开关（feature flags）的支持，允许不完整的功能存在于生产代码中而不影响用户。这种方法能够最大限度地减少合并冲突，并保持代码库始终处于可发布状态。

与主干开发相对的是长生命周期特性分支（long-lived feature branches），后者的使用会积累“合并债务”（merge debt），并延迟集成反馈，导致问题在后续合并中集中爆发。而主干开发通过小步快跑、持续集成的实践，将集成问题分散到日常开发中，降低了修复成本。

主干开发是持续交付（Continuous Delivery）和持续部署（Continuous Deployment）的基础实践之一。它要求开发者具备良好的单元测试习惯，并依赖功能开关管理未完成的特性，从而在不破坏主分支稳定性的前提下实现频繁合并。现代 CI/CD 工具（如 GitHub Actions、GitLab CI、Jenkins、CircleCI）对主干开发提供了天然支持，通过自动化构建和测试流水线快速验证每次合并的正确性。

## See also
- [[continuous-integration]]
- [[integration-testing]]
- [[code-review]]
