---
brief: 持续集成（CI）是自动构建和测试每次代码提交的实践，涵盖管道阶段、依赖管理、构建性能优化及持续交付/部署流程。
---

# 持续集成 (Continuous Integration)

> Source(s): raw/ch-03-Continuous Integration and Delivery

持续集成（Continuous Integration, CI）是软件工程中的核心实践，指在代码提交到版本控制后自动执行构建和测试。其核心理念是频繁集成变更（理想情况下每日多次），从而减少集成问题并尽早捕获错误。CI 起源于极限编程（Extreme Programming）运动，如今已成为行业标准，由 GitHub Actions、GitLab CI、Jenkins、CircleCI 等平台支持。

## CI 管道阶段

典型的 CI 管道包含以下阶段：

- **签出（Checkout）**：获取最新代码及子模块。
- **构建（Build）**：编译代码、安装依赖并生成构建产物（artifacts）。
- **测试（Test）**：运行单元测试、集成测试及其他自动化检查。
- **报告（Report）**：收集结果、生成覆盖率报告，并通知团队构建成功或失败。

现代 CI 系统支持并行作业执行、多环境矩阵构建（matrix builds）以及依赖缓存以加速管道运行。

## 主干开发与分支策略

**主干开发（Trunk-Based Development）** 是与 CI 良好互补的分支策略。开发者基于短期分支（理想情况下少于一天）工作，频繁合并到主分支（主干）。不完整的功能通过功能标志（feature flags）存在于生产代码中而不影响用户。这种方法最小化合并冲突，使代码库保持可发布状态。相比之下，长期特性分支会积累合并债务并延迟集成反馈。

## 持续交付与持续部署

**持续交付（Continuous Delivery）** 在 CI 基础上自动准备代码部署。通过 CI 检查后，代码被构建为可部署的产物（如 Docker 镜像、JAR 文件）并存储在制品仓库中。这些产物是不可变且版本化的，确保测试的内容即部署的内容。部署到预发布环境可能自动完成，而生产部署可能需要手动批准。

**持续部署（Continuous Deployment）** 更进一步：每个通过所有检查的变更自动部署到生产环境。这要求团队对测试和监控有高度信心，并具备成熟的回滚与回退（rollback/roll-forward）能力。通常，实践持续部署的组织会大量投资于可观测性、功能标志、金丝雀部署和自动回滚系统，以最小化有问题的变更的影响范围。

## Pipeline as Code

**管道即代码（Pipeline as Code）** 是将 CI/CD 管道定义在版本控制的配置文件中（例如 `.github/workflows/*.yml`、`Jenkinsfile`、`.gitlab-ci.yml`）。这使得管道变更可审查、可版本化和可重现。管道可以模板化并在仓库间共享，确保整个组织的一致实践。自定义动作（custom actions）和可复用工作流允许团队封装通用构建模式。

## 依赖管理

依赖管理是 CI 的关键关注点。过时的依赖可能包含安全漏洞，及时升级可减少破坏性变更的累积。工具如 Dependabot 和 Renovate 通过为新版本创建拉取请求来自动化依赖更新。这些自动化 PR 应触发完整的 CI 管道以验证兼容性。锁定文件（如 `package-lock.json`、`poetry.lock`、`Cargo.lock`）通过固定精确的依赖版本确保可重现构建。

## 构建性能优化

构建性能直接影响开发者生产力。慢速管道会导致上下文切换成本——开发者在等待时切换任务，并在结果返回时需重新投入。加快构建的策略包括：

- 缓存依赖
- 并行化独立的测试套件
- 使用构建产物避免重复工作
- 将测试分布到多台机器

一些组织维护专用的构建集群（build fleets），以确保所有团队获得一致、快速的 CI 执行。

## See also
- [[unit-testing]]
- [[integration-testing]]
- [[testing-pyramid]]
- [[code-review]]
