---
brief: 管道即代码是在版本控制配置文件中定义CI/CD管道的实践，使管道变更可审查、可版本化、可复现，支持模板化和跨仓库共享。
---

# Pipeline as Code

> Source(s): raw/ch-03-Continuous Integration and Delivery

**Pipeline as Code** is the practice of defining CI/CD pipelines in version-controlled configuration files (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`). This approach brings software engineering best practices to the pipeline definition itself: changes to the pipeline are subject to code review, versioned alongside the application code, and fully reproducible at any point in history. Pipelines can be templated and shared across repositories, ensuring consistent practices across an organization. Custom actions and reusable workflows allow teams to encapsulate common build patterns, reducing duplication and maintenance overhead.

In the context of modern Continuous Integration and Delivery (CI/CD), Pipeline as Code complements trunk-based development and automated testing. Pipeline definitions are stored in the project repository, so they evolve together with the codebase. The pipeline is typically triggered by events like pushes, pull requests, or scheduled intervals. Each stage (checkout, build, test, report) is declaratively described, and modern CI systems support parallel execution, matrix builds, and dependency caching to accelerate pipeline runs.

A key advantage of Pipeline as Code is traceability. Every modification to the pipeline is recorded in the version control history, enabling full audit trails and simple rollback if a change introduces a regression. Organizations can enforce governance by requiring pipeline changes to follow the same review process as application code.

Practices that closely integrate with Pipeline as Code include:
- **Continuous Integration**: automatically build and test on each commit.
- **Continuous Delivery**: automatically prepare deployable artifacts (e.g., Docker images, JAR files) after passing CI.
- **Continuous Deployment**: automatically deploy to production if all checks pass.
- **Dependency management**: tools like Dependabot and Renovate automate updates, and their pull requests trigger the pipeline for validation.
- **Build performance**: caching, parallelizing, and distributing tests to reduce feedback cycles.

Pipeline as Code enables teams to treat infrastructure and delivery automation as code, aligning with the DevOps principle of "everything as code."

## See also
- [[continuous-integration]]
- [[continuous-delivery]]
- [[trunk-based-development]]
- [[code-review]]
- [[integration-testing]]
- [[unit-testing]]
- [[testing-pyramid]]
