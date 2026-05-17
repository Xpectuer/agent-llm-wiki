---
brief: AlexNet是2012年ImageNet竞赛冠军模型，首次将ReLU和Dropout引入CNN，开启深度学习在计算机视觉的主流应用。
---

# AlexNet

> Source(s): raw/ch-01-Convolutional Neural Networks (CNNs)

**AlexNet** 是2012年由Alex Krizhevsky、Ilya Sutskever和Geoffrey Hinton提出的深度卷积神经网络架构。它在当年的ImageNet大规模视觉识别挑战赛（ILSVRC）中以显著优势夺冠，将top-5错误率从26.2%降至15.3%，这一突破性成果标志着深度学习正式进入主流计算机视觉领域，并引发了后续CNN研究的热潮。

## 核心创新

AlexNet的成功不仅在于网络深度，更在于引入了两项关键技术创新：

### ReLU激活函数

AlexNet首次在卷积神经网络中大规模应用 **ReLU**（Rectified Linear Unit，$f(x) = \max(0, x)$）作为隐藏层激活函数。相比当时主流的sigmoid和tanh激活函数，ReLU有效缓解了**梯度消失问题**，使得深层网络的训练成为可能，同时计算更为高效。

### Dropout正则化

AlexNet将 **Dropout** 引入CNN的全连接层，以概率 $p$（通常为0.5）随机丢弃神经元。这一技术强制网络学习冗余表示，有效防止过拟合，成为深度学习中的标准正则化手段。

## 网络结构特点

AlexNet的整体架构延续了 **LeNet-5** 奠定的"卷积-池化-全连接"基本范式，但规模大幅提升：

- 包含5个卷积层和3个全连接层
- 使用最大池化（Max Pooling）进行空间下采样
- 采用双GPU并行训练架构（受当时硬件显存限制）
- 局部响应归一化（Local Response Normalization, LRN）——虽然后续被 **Batch Normalization** 取代

## 历史意义与影响

AlexNet的 victory 证明了深度神经网络在复杂视觉任务上的巨大潜力，直接推动了：

- 计算机视觉研究从手工特征（如SIFT、HOG）向端到端深度学习范式的转变
- GPU在深度学习训练中的普及应用
- 后续更深、更高效的CNN架构涌现，如 **VGGNet**、**ResNet**、**EfficientNet** 等

## 训练方法

AlexNet的训练采用了当时标准的优化策略，包括：

- 小批量 **梯度下降**（mini-batch gradient descent）带动量优化器
- **数据增强**：随机裁剪、水平翻转、颜色抖动等
- **权重衰减**（L2正则化）与Dropout配合作为互补正则化手段

如今，**迁移学习** 从ImageNet预训练模型已成为大多数计算机视觉任务的标准做法，而AlexNet正是这一传统的开创者。

## See also
- [[[relu]]]
- [[[dropout]]]
- [[[lenet]]]
- [[[vggnet]]]
- [[[resnet]]]
- [[vision-transformer]]