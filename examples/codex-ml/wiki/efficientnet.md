---
brief: EfficientNet（2019）利用神经架构搜索同时优化深度、宽度和分辨率，实现高效的性能-计算权衡。
---

# EfficientNet

> Source(s): raw/ch-01-Convolutional Neural Networks (CNNs)

**EfficientNet** 是 Google 于 2019 年提出的卷积神经网络架构，其核心创新在于使用**神经架构搜索（Neural Architecture Search, NAS）**来同时优化网络的三个关键维度：**深度（depth）**、**宽度（width）**和**分辨率（resolution）**。这种联合缩放策略（compound scaling）打破了传统方法中仅单一维度扩展的局限，在计算效率与模型性能之间取得了更优的权衡。

## 核心思想

在 EfficientNet 之前，CNN 的扩展通常只关注单一维度：
- **深度扩展**：增加网络层数（如 [[resnet]] 从 18 层到 152 层）
- **宽度扩展**：增加每层的通道数
- **分辨率扩展**：提高输入图像的分辨率

EfficientNet 的研究者发现，这三个维度并非独立，而是相互关联的。通过神经架构搜索，EfficientNet 找到了一组最优的复合缩放系数，能够以固定的计算成本预算实现最佳性能。其基准网络 EfficientNet-B0 通过多目标优化搜索得到，随后使用复合缩放方法生成 B1 至 B7 等不同规模的变体。

## 与相关架构的对比

| 架构 | 年份 | 核心创新 | 扩展方式 |
|:---|:---|:---|:---|
| [[lenet]] / LeNet-5 | 1998 | 首个成功的 CNN，确立卷积-池化-全连接流程 | 浅层固定结构 |
| [[alexnet]] | 2012 | ReLU、Dropout，推动深度学习复兴 | 8 层固定结构 |
| [[vggnet]] | 2014 | 小卷积核（3×3）堆叠，证明深度重要性 | 深度单一扩展（16-19 层） |
| [[resnet]] | 2015 | 残差连接，解决梯度消失，支持百层网络 | 深度单一扩展 |
| **EfficientNet** | **2019** | **复合缩放，NAS 联合优化深度/宽度/分辨率** | **三维联合扩展** |

## 技术细节

EfficientNet 的复合缩放方法可以用以下公式描述：

- 深度：$d = \alpha^\phi$
- 宽度：$w = \beta^\phi$
- 分辨率：$r = \gamma^\phi$

其中 $\alpha, \beta, \gamma$ 是通过 NAS 确定的常数，$\phi$ 是用户指定的复合系数，用于控制整体计算资源。约束条件为 $\alpha \cdot \beta^2 \cdot \gamma^2 \approx 2$，且 $\alpha \geq 1, \beta \geq 1, \gamma \geq 1$。

## 影响与意义

EfficientNet 在 ImageNet 分类任务上展示了显著的效率优势：相比当时最先进的 CNN，它以更少的参数量和计算量（FLOPs）达到了更高的准确率。这一工作表明，**网络设计的优化空间不仅在于手工设计的拓扑结构，还在于系统化的扩展策略**。EfficientNet 的复合缩放思想也影响了后续的 EfficientNetV2（2021）等改进版本，以及在其他视觉任务（如目标检测、语义分割）中的应用。

## 训练与部署

EfficientNet 的训练遵循现代 CNN 的标准实践，包括：
- [[gradient-descent|带动量的随机梯度下降]]
- [[batch-normalization]] 稳定训练
- [[data-augmentation]] 增强泛化
- [[dropout]] 与权重衰减正则化
- [[transfer-learning]] 进行下游任务微调

## See also
- [[neural-architecture-search]]
- [[convolutional-neural-network]]
- [[resnet]]
- [[batch-normalization]]
- [[data-augmentation]]
- [[leaky-relu]]
