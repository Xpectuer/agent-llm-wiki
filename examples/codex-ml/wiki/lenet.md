---
brief: LeNet-5（1998）是首个成功的卷积神经网络，为手写数字识别设计，确立了卷积-池化-全连接的经典架构范式。
---

# LeNet

> Source(s): raw/ch-01-Convolutional Neural Networks (CNNs)

**LeNet-5** 是由 Yann LeCun 等人于 1998 年提出的卷积神经网络架构，被公认为第一个成功应用并广泛验证的 CNN。该网络专为手写数字识别任务设计，在 MNIST 等数据集上取得了优异性能，奠定了现代卷积神经网络的基础范式。

## 历史意义

LeNet-5 的核心贡献在于确立了 **卷积层（Convolution）→ 池化层（Pooling）→ 全连接层（Dense/FC）** 的标准流水线，这一架构模式至今仍是 CNN 设计的基石。它首次证明了基于梯度学习的卷积神经网络在复杂模式识别任务中的实用性和有效性。

## 架构特点

虽然原始材料的描述较为概括，但 LeNet-5 的典型结构包含：

- **卷积层**：使用可学习的局部感受野提取空间特征，通过权重共享大幅减少参数量
- **子采样（池化）层**：降低特征图空间维度，提供一定的平移不变性
- **全连接层**：将高层特征映射到最终分类输出

## 与现代架构的关联

LeNet-5 的设计思想直接影响了后续一系列里程碑式架构：

| 架构 | 年份 | 相对 LeNet-5 的关键演进 |
|:---|:---|:---|
| [[AlexNet]] | 2012 | 引入 [[relu]] 激活与 [[dropout]]，将深度学习带入主流计算机视觉 |
| [[VGGNet]] | 2014 | 使用更小的 3×3 卷积核堆叠更深的网络 |
| [[ResNet]] | 2015 | 通过跳跃连接解决深层网络训练难题 |
| [[EfficientNet]] | 2019 | 神经网络架构搜索实现深度、宽度、分辨率的联合优化 |

## 训练方法

LeNet-5 采用基于梯度下降的监督学习进行训练。现代 CNN 训练中广泛使用的技术均可视为对其原始方法的扩展与改进，包括：

- [[batch-normalization]]：稳定训练过程，允许更高学习率
- [[data-augmentation]]：增强数据多样性，改善泛化
- [[transfer-learning]]：利用预训练权重迁移至下游任务
- 各种优化器与学习率策略（如 [[learning-rate-schedule]]）

## 技术遗产

LeNet-5 所开创的 **局部连接（Local Connectivity）** 与 **权重共享（Weight Sharing）** 机制，至今仍是 [[convolutional-neural-network]] 区别于 [[recurrent-neural-network]] 和 [[transformer-architecture]] 等序列模型的核心特征。其针对二维空间结构数据的专门设计，使其在计算机视觉领域保持了长期的主导地位，直到 [[vision-transformer]] 等架构近年来提出新的可能性。

## See also
- [[convolutional-neural-network]]
- [[alexnet]]
- [[vggnet]]
- [[resnet]]
