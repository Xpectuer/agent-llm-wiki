---
brief: Vision Transformer (ViT) 将图像分割为 patches 作为 Token 输入 Transformer 架构，在大规模预训练下达到图像分类 SOTA。
---

# Vision Transformer (ViT)

> Source(s): raw/ch-03-Transformers and Attention Mechanisms

Vision Transformer (ViT) 是对经典 Transformer 架构的一种创新应用，它直接将图像处理为序列数据，绕过了传统卷积神经网络（CNN）中常用的卷积操作。ViT 的核心思想是将输入图像分割为固定大小的 patches（例如 16×16 像素），然后将每个 patch 展平并线性投影为一个 embedding，作为 Transformer 的输入 Token。这一设计使得 Transformer 能够像处理自然语言中的词元一样处理图像中的局部区域。

## Transformer 基础机制

ViT 所依赖的 Transformer 架构最初由 "Attention Is All You Need"（2017）提出，以自注意力机制取代了循环结构，实现了序列位置间的并行计算，显著提升了长序列的训练效率。

### 自注意力与多头注意力

自注意力通过计算序列中所有位置的加权和来捕获全局依赖，权重来源于位置间的兼容性分数：

```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

每个位置通过学习的线性投影生成三个向量：
- **Query (Q)**：查询向量，表示"我在寻找什么"
- **Key (K)**：键向量，表示"我包含什么"
- **Value (V)**：值向量，表示"我提供什么信息"

缩放因子 `1/√d_k` 防止点积过大导致 softmax 进入梯度极小的区域。

多头注意力（Multi-Head Attention）将 Q、K、V 投影到 `h` 个不同的子空间，并行计算注意力后再拼接结果，使模型能够同时关注不同表示子空间的信息。

### 位置编码

由于自注意力具有置换不变性，位置信息必须显式注入。原始 Transformer 使用正弦编码：

```
PE(pos, 2i) = sin(pos / 10000^{2i/d_model})
PE(pos, 2i+1) = cos(pos / 10000^{2i/d_model})
```

现代架构中也采用可学习的位置嵌入或相对位置编码（如 RoPE, Rotary Position Embedding）等替代方案。ViT 通常使用可学习的位置编码或正弦编码，以保留图像 patch 的空间顺序信息。

### 编码器架构

Transformer 编码器层由多头自注意力子层和逐位置前馈网络（Feed-Forward Network）组成，每个子层辅以层归一化（Layer Normalization）和残差连接。解码器则额外包含交叉注意力子层，但 ViT 仅使用编码器部分处理图像分类任务。

## ViT 的架构特点与优势

ViT 的关键优势在于其全局感受野：自注意力机制允许每个 patch 直接与所有其他 patch 交互，从而有效捕获长距离依赖关系，而在 CNN 中这通常需要深层堆叠才能实现。

然而，ViT 对大规模预训练数据集的依赖较强。在 ImageNet-21k 或 JFT-300M 等大型数据集上进行预训练后，ViT 在图像分类任务上可以达到或超越最先进的 CNN 模型（如 ResNet、EfficientNet）。当训练数据不足时，ViT 的归纳偏置较弱，性能可能不如同等规模的 CNN。

## Transformer 训练技术

Transformer 的训练需要精细的优化策略。原始配方采用 Adam 优化器配合 warmup 策略（前数千步线性增加学习率），随后接逆平方根衰减。权重衰减和 dropout 贯穿训练全程，梯度裁剪防止早期训练中的梯度范数不稳定，标签平滑（软化 one-hot 目标）则降低模型过度自信并改善泛化。

## 影响与变体

ViT 的成功推动了 Transformer 在计算机视觉领域的广泛推广，衍生出诸如 DeiT（使用知识蒸馏训练）、Swin Transformer（引入层级化窗口注意力）等变体。目前，ViT 已成为图像分类、目标检测、语义分割等视觉任务的流行基础架构。

## See also
- [[transformer-architecture]]
- [[convolutional-neural-network]]
- [[transfer-learning]]
- [[neural-architecture-search]]
