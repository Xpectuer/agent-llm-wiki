---
brief: 批归一化通过标准化层输入稳定深度网络训练，其mini-batch统计量引入的随机噪声还具有轻微正则化效果，可降低对显式正则化的需求。
---

# Batch Normalization

> Source(s): raw/simple-ml.md, raw/ch-01-Convolutional Neural Networks (CNNs), raw/ch-04-Regularization Techniques

**Batch Normalization（批归一化，简称 BatchNorm 或 BN）** 是一种用于深度神经网络的正则化与训练稳定技术，由 Sergey Ioffe 和 Christian Szegedy 于 2015 年提出。其核心思想是对每一层的输入进行标准化处理，使其保持零均值和单位方差，从而显著改善深层网络的训练动态。

## 核心机制

对于给定 mini-batch 的输入特征 $x$，Batch Normalization 执行以下变换：

$$\hat{x}_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}$$

$$y_i = \gamma \hat{x}_i + \beta$$

其中：
- $\mu_B$ 和 $\sigma_B^2$ 是当前 mini-batch 的均值和方差
- $\epsilon$ 是为数值稳定性添加的小常数（通常 $10^{-5}$）
- $\gamma$（缩放参数）和 $\beta$（偏移参数）是可学习的参数，允许网络恢复恒等映射

## 主要作用

### 减少内部协变量偏移（Internal Covariate Shift）

深层网络中，前面层的参数更新会改变后续层的输入分布，迫使后者不断适应新的分布。Batch Normalization 通过标准化层间激活值，稳定了这种分布变化，使各层可以相对独立地学习。

### 允许更高的学习率

传统深度网络需要使用较小的学习率以避免梯度爆炸或发散。标准化后的激活值具有更稳定的梯度流，使得训练可以使用更大的学习率，加速收敛过程。

### 降低对初始化的敏感性

良好的权重初始化对深度网络至关重要。Batch Normalization 使网络对初始权重的选择不那么敏感，减少了对精细调参的依赖。

### 正则化效果

Batch Normalization 的正则化效果来源于两个层面：

1. **mini-batch 统计噪声**：虽然 BN 的设计初衷是解决内部协变量偏移，但其依赖当前 mini-batch 计算均值和方差的过程引入了随机噪声——不同 mini-batch 的统计量存在自然波动，这种波动类似于 [[dropout]] 的随机失活机制，能够轻微地抑制过拟合，在某些场景下可降低对显式正则化技术（如 dropout 或权重衰减）的需求。

2. **标准化本身的约束**：将激活值约束在零均值、单位方差的分布范围内，间接限制了模型的表达能力，起到一定的容量控制作用。

需要注意的是，BN 的正则化效果相对温和，不能完全替代专门的正则化技术。在复杂任务或数据量有限的情况下，仍建议与 [[dropout]]、[[data-augmentation]]、权重衰减等方法配合使用。

## 训练与推理的差异

| 阶段 | 统计量来源 | 处理方式 |
|:---|:---|:---|
| **训练** | 当前 mini-batch | 实时计算 $\mu_B, \sigma_B^2$，并维护移动平均 |
| **推理** | 训练期累积的移动平均 | 使用固定的 $\mu_{moving}, \sigma_{moving}^2$ |

推理时使用移动平均统计量，确保输出确定性，避免依赖单个 batch 的随机性。

## 在优化器生态中的位置

Batch Normalization 与 [[gradient-descent]] 及其高级变体（如 Adam、RMSprop）协同工作，解决深层训练中的特定挑战：

- **配合 Momentum**：标准化后的稳定梯度使动量积累更可靠
- **配合高学习率**：BN 补偿了大学习率可能带来的不稳定性
- **缓解梯度消失/爆炸**：保持激活值在合理范围内，使反向传播更稳定

## 在 CNN 中的应用

Batch Normalization 在卷积神经网络（[[cnn]]）中具有尤为重要的地位。CNN 训练通常采用 mini-batch 梯度下降配合动量优化器，而 Batch Normalization 被应用于卷积层之后，通过将激活值归一化为零均值和单位方差来稳定训练。这种标准化使得 CNN 能够使用更高的学习率，并降低对权重初始化的敏感性，与数据增强、权重衰减（L2 正则化）和 [[dropout]] 等技术形成互补的正则化体系。

在 CNN 中的具体实践包括：
- **按通道归一化**：对 CNN 通常按通道维度计算统计量，即每个特征通道有独立的 $\gamma, \beta$
- **典型放置位置**：置于卷积层之后、激活函数（如 [[relu]]）之前；也可根据具体架构调整

## 变体与扩展

| 变体 | 适用场景 | 核心区别 |
|:---|:---|:---|
| **Layer Normalization** | 循环神经网络、Transformer | 对单样本的所有特征归一化，不依赖 batch 维度 |
| **Instance Normalization** | 风格迁移、图像生成 | 对每个样本的每个通道单独归一化 |
| **Group Normalization** | 小 batch 训练 | 将通道分组后在组内归一化 |
| **Switchable Normalization** | 通用框架 | 自适应学习不同归一化方式的组合权重 |

## 实际应用要点

- **放置位置**：通常置于线性/卷积层之后、激活函数之前；也可置于激活函数之后（视具体架构而定）
- **与卷积层的配合**：对 CNN 通常按通道维度计算统计量，即每个特征通道有独立的 $\gamma, \beta$
- **Batch size 敏感性**：过小的 batch size（如 < 16）会导致统计量估计不准，此时可考虑 [[layer-normalization]] 或 Group Normalization；同时，batch size 越小，mini-batch 统计噪声越大，正则化效果越强，但训练稳定性可能下降
- **不适用于所有层**：部分输出层（如某些生成模型的输出）可能不需要标准化

## 历史与影响

Batch Normalization 的提出标志着现代深度学习训练技术的重要里程碑。它使得训练深度超过 100 层的网络成为常规实践，并催生了 ResNet 等极深架构的成功。其设计理念——通过显式控制网络内部激活分布来简化优化——影响了后续大量归一化技术的开发。

## See also
- [[regularization]]
- [[layer-normalization]]
- [[residual-connection]]
- [[relu]]
- [[transfer-learning]]
- [[gradient-descent]]
