---
brief: ResNet（2015）通过跳跃连接的残差块解决深层网络训练难题，实现100+层网络的可训练性。
---

# ResNet

> Source(s): raw/ch-01-Convolutional Neural Networks (CNNs)

ResNet（Residual Network，残差网络）是2015年由何恺明等人提出的深度卷积神经网络架构，其核心创新在于引入了**跳跃连接（skip connections）** 的**残差块（residual blocks）**，使梯度能够直接流过网络，从而解决了深层网络中的梯度消失问题，首次实现了100层以上网络的有效训练。

## 核心思想

ResNet 的关键洞见是：与其让网络直接学习从输入到输出的映射 $H(x)$，不如让网络学习残差函数 $F(x) = H(x) - x$，即输入与输出之间的差异。原始映射则通过恒等连接（identity connection）恢复为 $H(x) = F(x) + x$。

这种设计允许网络在必要时选择"跳过"某些层——如果残差 $F(x)$ 趋近于零，则该层近似执行恒等映射。这为深层网络提供了自然的退化保护机制：增加更多层不会导致性能下降，因为网络可以简单地学习恒等映射。

## 残差块结构

残差块包含两条路径：
- **主路径**：一个或多个卷积层、批归一化和激活函数的组合
- **跳跃连接**：将输入 $x$ 直接加到主路径的输出上

当输入与输出的维度不匹配时，跳跃连接可通过1×1卷积进行线性投影来调整维度。

## 历史意义与影响

在 ResNet 之前，网络深度的增加往往导致训练精度下降——这并非过拟合，而是优化困难（退化问题）。VGGNet 虽证明了深度的重要性，但其16-19层已接近可训练极限。ResNet 通过残差学习突破了这一瓶颈，成功训练了152层甚至超过1000层的网络，在2015年ImageNet竞赛中以显著优势夺冠。

ResNet 的跳跃连接思想已成为现代深度学习的基石设计模式，影响了包括 DenseNet、U-Net、Transformer 在内的众多后续架构。其"学习残差而非直接映射"的哲学也启发了其他领域的网络设计。

## 与其他架构的关系

| 架构 | 年份 | 与 ResNet 的对比 |
|:---|:---|:---|
| [[lenet]] | 1998 | 开创性CNN，仅5层，无残差概念 |
| [[alexnet]] | 2012 | 引入ReLU和dropout，8层深度 |
| [[vggnet]] | 2014 | 证明深度重要性，16-19层，无跳跃连接 |
| ResNet | 2015 | 跳跃连接解决梯度流问题，100+层 |
| EfficientNet | 2019 | 结合残差块与神经架构搜索优化缩放 |

## 技术细节关联

ResNet 的训练依赖多项关键技术：
- **[[relu]]** 及其变体（[[leaky-relu]]、[[prelu]]、[[elu]]）作为激活函数
- **[[batch-normalization]]** 稳定深层网络的训练分布
- **[[dropout]]** 与权重衰减作为正则化手段
- **[[data-augmentation]]** 提升泛化能力
- **[[gradient-descent]]** 配合动量优化器进行参数更新

## 现代应用

ResNet 及其变体（ResNeXt、Wide ResNet、ResNet-D等）至今仍是计算机视觉的主流骨干网络。通过 **[[transfer-learning]]**，ImageNet 预训练的 ResNet 被广泛用于目标检测、语义分割、医学影像等下游任务，成为视觉领域的标准特征提取器。

## See also
- [[convolutional-neural-network]]
- [[vggnet]]
- [[batch-normalization]]
- [[residual-connection]]
- [[densenet]]
- [[transformer-architecture]]