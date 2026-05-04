# Queries

> Record of questions asked against the wiki with their answers and citations.

<!-- Add query records here using the format:
## [date] question
**Answer**: ...
**Citations**: [[page]] — what was cited
**Raw sources**: raw/file
-->

## [2026-05-04] Transformer和BERT有什么区别？

**回答**: 信息不足以回答。当前提供的 wiki 页面为空（没有找到相关页面），且未提供任何原始参考材料，因此无法基于现有知识库内容为您解答“Transformer和BERT有什么区别”。

**引用**:
- (无相关引用)

**建议新页面**: 
- **建议页面名称**: `[[Transformer_vs_BERT]]`
- **内容摘要**: 建议在此页面中梳理和记录 Transformer 与 BERT 的核心区别。内容可包括：1. 架构差异（Transformer 包含完整的 Encoder 和 Decoder，而 BERT 仅使用了 Transformer 的 Encoder 部分）；2. 核心机制差异（Transformer 侧重于 Seq2Seq 的自回归生成，BERT 侧重于双向掩码语言模型）；3. 预训练任务差异（BERT 使用了掩码语言模型 MLM 和下一句预测 NSP）；4. 适用场景（Transformer 常用于机器翻译等生成任务，BERT 常用于文本分类、命名实体识别等 NLU 理解任务）。

---

## [2026-05-04] Transformer和BERT有什么区别？

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

---
