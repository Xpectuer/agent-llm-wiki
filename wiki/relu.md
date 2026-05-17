---
brief: ReLU（f(x)=max(0,x)）是CNN隐藏层的标准激活函数，解决了梯度消失问题，并有多种改进变体。
---

# ReLU

> Source(s): raw/ch-01-Convolutional Neural Networks (CNNs)

**ReLU**（Rectified Linear Unit，修正线性单元）是一种广泛应用于深度神经网络的激活函数，其数学定义为：

$$f(x) = \max(0, x)$$

即：当输入为正时输出原值，输入为负时输出零。

## 核心特性与优势

ReLU 成为 [[convolutional-neural-network|卷积神经网络]]（CNN）隐藏层标准选择的主要原因：

| 特性 | 说明 |
|:---|:---|
| **计算简单** | 仅需阈值比较，无指数运算，前向/反向传播效率高 |
| **缓解梯度消失** | 正区间梯度恒为 1，避免了 [[sigmoid]] 和 [[tanh]] 在深层网络中的梯度饱和问题 |
| **稀疏激活** | 负值区域输出为零，使网络产生稀疏表示，提升计算效率 |

## 历史引入

ReLU 在 CNN 中的普及始于 **[[alexnet|AlexNet (2012)]]**。该架构首次将 ReLU 大规模应用于卷积神经网络，并配合 [[dropout]] 正则化，以显著优势赢得 ImageNet 竞赛，由此推动深度学习进入计算机视觉主流。

## 变体与改进

针对 ReLU 的 **"dying ReLU" 问题**（神经元永久失活，负区间梯度为零），研究者提出了多种改进变体：

- **Leaky ReLU**：负区间引入微小斜率 α（如 0.01），$f(x) = \max(\alpha x, x)$
- **PReLU（Parametric ReLU）**：将负区间斜率设为可学习参数
- **ELU（Exponential Linear Unit）**：负区间使用指数函数平滑过渡，输出均值更接近零

## 在 CNN 架构中的位置

ReLU 通常应用于：
1. **卷积层之后**：对特征图（feature maps）进行非线性变换
2. **批归一化之后**：现代架构常采用 Conv → [[batch-normalization|BatchNorm]] → ReLU 的顺序

与 [[batch-normalization|批归一化]] 协同使用时，ReLU 能够稳定深层网络的训练过程，支持更高的学习率。

## 与其他激活函数的对比

| 激活函数 | 公式 | 主要问题 |
|:---|:---|:---|
| Sigmoid | $\sigma(x) = \frac{1}{1+e^{-x}}$ | 两端饱和，梯度消失严重 |
| Tanh | $\tanh(x)$ | 仍存在梯度饱和，零中心化但未解决根本问题 |
| **ReLU** | $\max(0,x)$ | **dying ReLU**，负区间信息丢失 |
| Leaky ReLU / PReLU / ELU | 见上文 | 缓解 dying ReLU，引入额外超参数或计算成本 |

## See also
- [[[[leaky-relu]]]]
- [[[[prelu]]]]
- [[[[elu]]]]
- [[[[activation-function]]]]
- [[[[gradient-vanishing-problem]]]]
- [[gradient-descent]]
