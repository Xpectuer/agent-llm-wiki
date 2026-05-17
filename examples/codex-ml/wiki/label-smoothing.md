---
brief: 标签平滑是一种正则化技术，通过将one-hot目标标签替换为软标签来降低模型过置信度，提升泛化能力。
---

# Label Smoothing

> Source(s): raw/ch-03-Transformers and Attention Mechanisms

**标签平滑（Label Smoothing）** 是一种用于训练深度神经网络的正则化技术，通过将硬性的 one-hot 目标标签替换为"软标签"（soft targets），来降低模型的过置信度（overconfidence），从而改善模型的泛化能力。

## 核心思想

在标准的分类任务中，模型通常使用 one-hot 编码的目标标签进行训练，即正确类别的概率为 1，其余所有类别的概率为 0。这种硬性标签会鼓励模型对正确类别输出极高的置信度（softmax 概率接近 1），即使对于模糊或困难的样本也是如此。标签平滑通过将目标分布从 one-hot 调整为：

$$q'(k|x) = (1 - \epsilon) \cdot q(k|x) + \epsilon / K$$

其中 $q(k|x)$ 是原始的 one-hot 标签，$K$ 是类别总数，$\epsilon$ 是一个小的平滑超参数（通常取 0.1）。这样，正确类别的概率略低于 1，而所有错误类别则分摊剩余的小部分概率。

## 主要作用

- **降低过置信度**：防止模型对训练样本输出过于极端的概率分布
- **改善泛化**：平滑的目标分布相当于对模型施加正则化，减少过拟合
- **提升校准**：使模型的预测概率更好地反映真实的置信水平
- **增强鲁棒性**：对标签噪声更具容忍度

## 在 Transformer 训练中的应用

标签平滑是训练现代 Transformer 模型的标准技术之一。在原始 Transformer 论文 "Attention Is All You Need" 的训练配置中，标签平滑与 Adam 优化器、学习率预热（warmup）、权重衰减和 dropout 等技术共同使用，以确保训练稳定性和最终性能。具体而言，标签平滑通过软化序列到序列任务中的目标 token 分布，帮助模型在机器翻译等任务上获得更好的 BLEU 分数。

## 与其他正则化技术的关系

标签平滑常与以下技术配合使用或作为替代方案：
- **Dropout**：随机丢弃神经元以防止共适应
- **权重衰减（Weight Decay）**：对参数施加 L2 惩罚
- **知识蒸馏（Knowledge Distillation）**：使用教师模型的软标签作为目标，标签平滑可视为一种"无教师"的蒸馏形式

## 注意事项

虽然标签平滑通常有益，但在某些场景下需谨慎使用：
- 与知识蒸馏联合使用时可能产生冲突（学生模型难以匹配已平滑的教师分布）
- 在需要精确概率估计的某些下游任务中可能略微损害性能

## See also
- [[regularization]]
- [[dropout]]
- [[knowledge-distillation]]
- [[transformer-architecture]]
- [[data-augmentation]]
