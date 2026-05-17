---
brief: Transformer 是一种基于自注意力机制的神经网络架构，通过并行处理序列位置取代循环结构，显著提升了长序列的训练效率。
---

# Transformer Architecture

> Source(s): raw/ch-03-Transformers and Attention Mechanisms

Transformer 架构于 2017 年由 "Attention Is All You Need" 论文提出，通过自注意力机制取代了循环结构，实现了序列位置上的并行计算，从而极大地提升了长序列的训练效率。

## 自注意力机制 (Self-Attention)

自注意力机制计算序列中所有位置的加权和，其中权重由位置之间的兼容性分数得出：

```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

每个位置通过学习的线性投影生成三个向量：
- **查询 (Query, Q)**：我在寻找什么？
- **键 (Key, K)**：我包含什么信息？
- **值 (Value, V)**：我提供什么信息？

缩放因子 `1/√d_k` 防止点积值过大，避免 softmax 进入梯度极小区域。

## 多头注意力 (Multi-Head Attention)

多头注意力不是仅计算单个注意力函数，而是将 Q、K、V 投影到 `h` 个不同的子空间，并行计算注意力结果，然后拼接输出。这使得模型能够同时从不同表示子空间中关注信息，增强了模型捕获多种关系的能力。

## 位置编码 (Positional Encoding)

由于自注意力机制是置换不变的，必须显式注入位置信息。原始 Transformer 使用正弦编码：

```
PE(pos, 2i) = sin(pos / 10000^{2i/d_model})
PE(pos, 2i+1) = cos(pos / 10000^{2i/d_model})
```

学习的位置嵌入和相对位置编码（如旋转位置嵌入 RoPE）是现代架构中常用的替代方案。

## 架构组成

Transformer 由堆叠的编码器层和解码器层组成。每个编码器层包含一个多头自注意力子层和一个逐位置的前馈网络（position-wise feed-forward network）。每个解码器层在编码器层基础上增加一个交叉注意力子层，用于关注编码器输出。层归一化（Layer Normalization）和残差连接（Residual Connection）包裹每个子层。

## 重要变体

- **BERT**：双向编码器，使用掩码语言模型（预测随机掩码的 token）和下一句预测进行预训练，擅长理解任务。
- **GPT 系列**：自回归解码器，根据前文预测下一个 token。GPT-3 展示了扩大模型规模和数据的涌现能力。GPT-4 增加了多模态输入能力。详见 [[gpt-series]]。
- **Vision Transformer (ViT)**：将 Transformer 直接应用于图像块（视为 token），在大数据集上预训练后，在图像分类任务上取得领先效果。

## 训练要点

Transformer 训练需要谨慎的优化策略：

- **优化器**：通常使用 Adam 优化器，并配合 **warmup** 策略（前几千步线性增加学习率），之后按 **逆平方根衰减**（inverse square root decay）降低学习率。
- **正则化**：全程使用权重衰减（Weight Decay）和 Dropout。
- **梯度裁剪**（Gradient Clipping）：防止早期训练因梯度范数过大导致的不稳定。
- **标签平滑**（Label Smoothing）：软化 one-hot 目标标签，减少过置信度，提升泛化能力。

## See also
- [[rotary-position-embedding]]
- [[recurrent-neural-network]]
