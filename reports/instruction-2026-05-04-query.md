# Query-Generated Page Suggestion (2026-05-04)

**回答**:
Transformer 和 BERT 的主要区别在于它们的定位与使用的架构模块不同：
1. **整体与局部的关系**：Transformer 是一种基础的深度学习架构，由 Vaswani 等人在 2017 年提出；而 BERT 是由 Google 在 2018 年提出的一个具体的预训练语言模型，它的核心架构正是基于 Transformer 构建的。
2. **架构模块的选择**：Transformer 包含编码器和解码器两部分。BERT 仅仅使用了 Transformer 的**编码器**部分来进行模型构建。
3. **训练任务的不同**：Transformer 是一种基础架构，而 BERT 在此基础上定义了特定的预训练任务，即通过“掩码语言模型”和“下一句预测”这两个任务来学习双向的语义表示和句子级别的连贯性。

**引用**:
- [[transformer]] — 引用了 Transformer 的提出时间、基础架构定义，以及 BERT 使用了其编码器部分并采用掩码语言模型和下一句预测任务的信息。
- [[bert]] — 引用了 BERT 的提出时间、基于 Transformer 架构构建，以及仅使用 Transformer 编码器部分和特定预训练任务的详细说明。
- raw/test-transformer.txt — 引用了上述关于 Transformer 架构和 BERT 模型特性的原始记录材料。

**建议新页面**:
建议创建新页面：【Transformer-vs-BERT】
**内容摘要**：总结和对比基础架构 Transformer 与预训练模型 BERT 之间的核心区别，包括架构层面（完整架构 vs 仅使用编码器）和应用/训练层面（基础架构 vs 包含特定预训练任务如掩码语言模型和下一句预测的下游模型）的详细对比。

## Action Required
- Review the suggested new page above
- If valuable, create the wiki page using `wiki convert` or manually
