---
brief: BERT是双向编码器Transformer，通过掩码语言建模和下一句预测进行预训练，擅长自然语言理解任务。
---

# BERT

> Source(s): raw/ch-03-Transformers and Attention Mechanisms

BERT（Bidirectional Encoder Representations from Transformers）是一种基于Transformer架构的双向编码器模型，由Google于2018年提出。与自回归的语言模型（如GPT系列）不同，BERT通过双向上下文同时理解输入文本的左右两侧信息，使其在自然语言理解任务上表现优异。

## 核心机制：自注意力

BERT基于Transformer的编码器结构，其核心是自注意力机制（Self-Attention）。自注意力通过计算序列中所有位置间的兼容性分数，生成加权表示：

```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

每个位置通过学习的线性投影生成三个向量：
- **Query (Q)**：表示"我在寻找什么"
- **Key (K)**：表示"我包含什么"
- **Value (V)**：表示"我提供什么信息"

缩放因子 `1/√d_k` 防止点积过大导致softmax进入梯度极小的区域。BERT采用**多头注意力（Multi-Head Attention）**，将Q、K、V投影到多个子空间并行计算注意力，使模型能够同时关注不同表示子空间的信息。

## 预训练任务

BERT的预训练过程包含两个核心任务：

1. **掩码语言建模（Masked Language Modeling）**：随机掩盖输入序列中的部分词汇（通常15%），让模型根据上下文预测被掩盖的词汇。这迫使模型学习深度的双向上下文表示，区别于GPT等自回归模型的单向建模。

2. **下一句预测（Next Sentence Prediction）**：给定两个句子，判断后者是否是前者的下一句。该任务帮助模型理解句子间的关系，对问答、推理等任务至关重要。

## 架构特点

- 仅使用Transformer的**编码器（Encoder）**部分，堆叠多层双向自注意力层（Base版12层，Large版24层）。
- 使用**位置编码**注入序列顺序信息。原始BERT采用可学习的位置嵌入，而Transformer原始论文使用正弦/余弦编码：
  ```
  PE(pos, 2i) = sin(pos / 10000^{2i/d_model})
  PE(pos, 2i+1) = cos(pos / 10000^{2i/d_model})
  ```
  现代变体还包括相对位置编码（如RoPE）等替代方案。
- 每层编码器包含多头自注意力子层和前馈网络子层，由层归一化（Layer Normalization）和残差连接包裹。

## 与GPT的对比

| 特性 | BERT | GPT系列 |
|------|------|---------|
| 架构 | 编码器（双向） | 解码器（自回归） |
| 预训练目标 | 掩码语言建模 + 下一句预测 | 下一个词预测 |
| 注意力机制 | 双向自注意力 | 掩码自注意力（仅左侧上下文） |
| 擅长领域 | 理解任务（分类、问答、NER） | 生成任务（文本续写、对话） |

## 影响与地位

BERT在2018年发布后，迅速成为自然语言处理领域的基线模型，刷新了多项榜单。其双向编码思想影响了许多后续模型（如RoBERTa、ALBERT、DistilBERT）。BERT证明了深度预训练语言模型在理解任务上的巨大潜力，也为后来大型语言模型（LLM）的发展奠定了基础。

## 训练细节

BERT训练遵循Transformer的标准优化配置：
- **Adam优化器**配合**学习率预热（warmup）**——前数千步线性增加学习率，随后采用**逆平方根衰减**。
- **梯度裁剪**防止早期训练中的梯度爆炸，确保训练稳定性。
- **标签平滑（label smoothing）**软化one-hot目标，减少过拟合并改善泛化。
- **Dropout**和**权重衰减（weight decay）**贯穿训练过程以增强正则化效果。

## See also
- [[positional-encoding]]
- [[dropout]]
- [[learning-rate-schedule]]
- [[transfer-learning]]
- [[codex-cli]]
- [[multi-head-attention]]