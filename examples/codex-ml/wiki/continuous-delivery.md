---
brief: 持续交付在CI基础上自动将代码构建为不可变的、版本化的部署制品并存入制品仓库，持续部署则进一步将每项通过所有检查的变更自动部署到生产环境。
---

# Continuous Delivery

> Source(s): raw/ch-03-Continuous Integration and Delivery

Continuous Delivery 是持续集成（CI）的自然延伸，它自动为部署准备代码。在 CI 检查通过后，代码被构建成可部署的制品（如 Docker 镜像、JAR 文件等），并存储到制品仓库中。这些制品是不可变且带有版本号的，确保测试时的内容与最终部署的内容完全一致。部署到预发（staging）环境通常是自动完成的，而生产环境部署可能需要手动批准。

Continuous Deployment（持续部署）则是更进一步：每一项通过所有检查的代码变更都会被自动部署到生产环境。这要求对测试和监控有极高的信心，同时需要成熟的回滚和前滚能力。实践持续部署的组织通常会在可观测性、特性开关、金丝雀部署和自动回滚系统上投入大量精力，以最小化任何有问题变更的影响范围。

## Pipeline as Code

Pipeline as Code 是指将 CI/CD 流水线的定义放在版本控制的配置文件（如 `.github/workflows/*.yml`、`Jenkinsfile`、`.gitlab-ci.yml`）中。这使得流水线变更是可审查、可版本控制且可重现的。流水线可以在不同仓库间进行模板化和共享，确保整个组织的一致性。自定义 actions 和可重用工作流允许团队封装常见的构建模式。

## 依赖管理

依赖管理是 CI 中一个关键关注点。过时的依赖可能包含安全漏洞，及时升级它们可以减少破坏性变更的累积。像 Dependabot 和 Renovate 这样的工具通过为新版本创建 pull request 来自动化依赖更新。这些自动化的 PR 应触发完整的 CI 流水线以验证兼容性。锁文件（如 `package-lock.json`、`poetry.lock`、`Cargo.lock`）通过固定精确的依赖版本来确保可重现的构建。

## 构建性能

构建性能直接影响开发者的生产力。缓慢的流水线会造成上下文切换成本——开发者在等待结果时会转向其他任务，当结果返回时又需要重新投入。加速构建的策略包括：缓存依赖、并行化独立测试套件、使用构建制品避免重复工作、以及在多台机器上分布式运行测试。一些组织会维护专用的构建集群，以确保所有团队都能获得一致且快速的 CI 执行。

## 与持续集成的关联

持续交付建立在持续集成的基础之上。典型的 CI 流水线包含 checkout（检出）、build（构建）、test（测试）和 report（报告）等阶段。Trunk-Based Development（主干开发）是与 CI 互补的分支策略：开发者在短期分支（最好不超过一天）上工作，频繁合并到主分支，并通过特性开关允许不完整的功能存在于生产代码中而不影响用户。这种方式能最小化合并冲突，并保持代码库处于可发布状态。

## See also
- [[continuous-integration]]
- [[trunk-based-development]]
- [[integration-testing]]
- [[unit-testing]]
- [[testing-pyramid]]
- [[code-review]]
