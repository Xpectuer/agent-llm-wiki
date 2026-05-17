---
brief: 正则化是防止神经网络过拟合、提升模型泛化能力的策略集合，涵盖L1/L2正则化、Dropout、数据增强、早停法等技术。
---

# Regularization

> Source(s): raw/ch-04-Regularization Techniques

**Regularization**（正则化） encompasses strategies to prevent overfitting and improve model generalization. These techniques are applicable across all neural network architectures and form a critical part of deep learning practice.

## L1 and L2 Regularization

**L2 regularization**（weight decay） adds `λ Σ w_i²` to the loss function, penalizing large weights and encouraging distributed representations. **L1 regularization** adds `λ Σ |w_i|`, producing sparse weights as a form of feature selection. In practice, L2 is more common in deep learning, while L1 is used when sparsity is explicitly desired.

## Dropout

[[dropout]] randomly deactivates a fraction `p` of neurons during each training iteration, forcing the network to learn redundant and robust features. At inference, all neurons are active but their outputs are scaled by `(1 - p)` to maintain expected values. Common rates are 0.2 for input layers, 0.5 for hidden layers.

Variants include:
- **Spatial Dropout**: Drops entire feature maps in [[convolutional-neural-network|CNNs]] rather than individual activations
- **DropConnect**: Drops individual weights rather than activations
- **Stochastic Depth**: Randomly drops entire layers during training, crucial for training very deep networks like [[resnet]]

## Data Augmentation

Expanding the training set through label-preserving transformations acts as a powerful regularizer. See [[data-augmentation]] for detailed discussion.

Key techniques by modality:
- **Images**: Random crops, flips, rotations, color jitter, Cutout, Mixup, CutMix
- **Text**: Back-translation, synonym replacement, random insertion/deletion, word swapping
- **Audio**: Time stretching, pitch shifting, adding noise, SpecAugment

**Mixup** creates synthetic training examples by convex combination: `x̃ = λx_i + (1-λ)x_j`, `ỹ = λy_i + (1-λ)y_j`, encouraging linear behavior between training points.

## Early Stopping

Monitor validation loss during training and stop when it ceases to improve (with patience to allow for temporary plateaus). This prevents the model from memorizing training noise. Early stopping is almost universally applied in practice due to its simplicity and effectiveness.

## Batch Normalization as Regularizer

While designed to address internal covariate shift, [[batch-normalization]] has a mild regularizing effect. The noise introduced by batch statistics (which vary per mini-batch) acts similarly to dropout, reducing the need for explicit regularization in some cases.

## See also
- [[dropout]]
- [[data-augmentation]]
- [[batch-normalization]]
- [[label-smoothing]]
- [[early-stopping]]
- [[transfer-learning]]
