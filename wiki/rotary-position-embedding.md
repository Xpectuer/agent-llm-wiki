---
brief: 旋转位置编码（RoPE）是一种通过旋转矩阵将位置信息编码到查询和键向量中的相对位置编码方法，被现代大语言模型广泛采用。
---

# Rotary Position Embedding (RoPE)

> Source(s): raw/ch-03-Transformers and Attention Mechanisms

**旋转位置编码**（Rotary Position Embedding，简称 **RoPE**）是一种相对位置编码方法，通过旋转矩阵将位置信息直接编码到自注意力机制中的查询（Query）和键（Key）向量中。RoPE 是现代大语言模型中广泛采用的位置编码方案之一，作为原始正弦位置编码和可学习位置嵌入的替代方案。

## 背景：Transformer 中的位置编码需求

Transformer 架构的核心自注意力机制具有**置换不变性**（permutation-invariant）——即对输入序列的顺序不敏感。因此，位置信息必须显式注入模型。原始 Transformer 采用正弦位置编码：

```
PE(pos, 2i) = sin(pos / 10000^{2i/d_model})
PE(pos, 2i+1) = cos(pos / 10000^{2i/d_model})
```

此外，可学习的位置嵌入（learned positional embeddings）也是早期常用的替代方案。RoPE 在此基础上提供了更优雅的相对位置建模方式。

## RoPE 的核心思想

与将位置信息作为附加输入不同，RoPE **通过旋转矩阵将位置信息直接融合到 Q 和 K 向量的内积计算中**。具体而言：

- 对于序列中位置为 $m$ 的查询向量 $q_m$ 和位置为 $n$ 的键向量 $k_n$，RoPE 通过旋转变换 $R_{\Theta,m}$ 和 $R_{\Theta,n}$ 分别作用于两者
- 变换后的内积 $\langle R_{\Theta,m} q_m, R_{\Theta,n} k_n \rangle$ 仅依赖于相对位置 $m - n$，即满足 **相对位置编码** 的性质
- 该内积随着相对距离 $|m - n|$ 的增大而衰减，体现了"远距离位置关联性减弱"的归纳偏置

## 旋转矩阵的构造

RoPE 将向量空间划分为若干二维子空间，在每个子空间内独立旋转。对于维度 $d$，旋转角度与位置索引 $m$ 成正比：

$$\theta_i = 10000^{-2i/d}$$

位置 $m$ 处的旋转矩阵为分块对角矩阵，每块为二维旋转矩阵：

$$R_{\Theta,m} = \begin{pmatrix} \cos m\theta_1 & -\sin m\theta_1 & 0 & 0 & \cdots \\ \sin m\theta_1 & \cos m\theta_1 & 0 & 0 & \cdots \\ 0 & 0 & \cos m\theta_2 & -\sin m\theta_2 & \cdots \\ 0 & 0 & \sin m\theta_2 & \cos m\theta_2 & \cdots \\ \vdots & \vdots & \vdots & \vdots & \ddots \end{pmatrix}$$

## 优势与特点

| 特性 | 说明 |
|------|------|
| **相对位置感知** | 内积天然体现相对位置关系，无需显式计算位置偏置矩阵 |
| **远程衰减** | 随着相对距离增大，内积幅值自然衰减 |
| **与注意力兼容** | 直接融入标准自注意力计算框架，无需修改架构 |
| **外推能力** | 旋转角度的连续性使模型对训练时未见过的序列长度具有一定泛化能力 |
| **计算效率** | 可通过复数乘法或高效矩阵运算实现， overhead 较小 |

## 应用与影响

RoPE 自提出后被众多现代大语言模型采用，包括 LLaMA、PaLM、ChatGLM 等主流架构。其成功验证了**将位置信息编码到注意力内积空间**这一思路的有效性，推动了相对位置编码研究的进一步发展。后续工作如 **NTK-aware scaling**、**YaRN** 等均在 RoPE 基础上扩展了长上下文外推能力。

## See also
- [[positional-encoding]]
- [[attention-mechanism]]
- [[transformer-architecture]]
- [[multi-head-attention]]
- [[large-language-model]]
- [[dropout]]
