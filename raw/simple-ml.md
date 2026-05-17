# Gradient Descent Optimization

> A fundamental optimization algorithm for training machine learning models.

## Overview

Gradient descent is an iterative optimization algorithm used to minimize a loss function by updating model parameters in the opposite direction of the gradient. It is the backbone of modern machine learning, powering everything from linear regression to deep neural networks.

At its core, gradient descent answers the question: given a function `J(θ)`, how do we find the parameters `θ` that minimize `J`? The algorithm works by taking repeated steps proportional to the negative of the gradient:

```
θ_{t+1} = θ_t - η ∇J(θ_t)
```

where `η` (eta) is the learning rate, a hyperparameter controlling step size.

## Variants

### Batch Gradient Descent

Computes the gradient using the entire training dataset. This gives an accurate estimate of the true gradient but becomes computationally expensive for large datasets. Each parameter update requires processing all N training examples.

**Advantages**: Stable convergence, guaranteed to reach local minimum for convex functions.
**Disadvantages**: Intractable for large datasets, slow per-epoch progress.

### Stochastic Gradient Descent (SGD)

Updates parameters using a single randomly selected training example at each step. This introduces noise into the gradient estimate, which can help escape local minima but causes the loss to fluctuate.

```
θ_{t+1} = θ_t - η ∇J(θ_t; x_i, y_i)
```

**Advantages**: Fast per-iteration, works with streaming/online data, can escape local minima.
**Disadvantages**: High variance in updates, may require learning rate annealing.

### Mini-batch Gradient Descent

A compromise between batch and stochastic: updates use a small random subset (mini-batch) of the training data, typically 32-512 examples. This is the workhorse of deep learning training, balancing computational efficiency with gradient accuracy.

**Advantages**: Leverages vectorized operations on GPUs, more stable than SGD, faster than batch.
**Disadvantages**: Introduces a new hyperparameter (batch size).

## Advanced Optimizers

### Momentum

Momentum accumulates a velocity vector of past gradients to smooth updates and accelerate convergence in directions with consistent gradients. The update rule:

```
v_t = γ v_{t-1} + η ∇J(θ_t)
θ_{t+1} = θ_t - v_t
```

where `γ` (typically 0.9) controls the momentum decay. Momentum helps navigate ravines in the loss landscape and dampens oscillations.

### RMSprop

RMSprop adapts the learning rate for each parameter by dividing the gradient by a running average of its recent magnitude. This prevents the learning rate from becoming too small for parameters with consistently small gradients.

```
E[g²]_t = β E[g²]_{t-1} + (1 - β) g_t²
θ_{t+1} = θ_t - (η / √(E[g²]_t + ε)) g_t
```

### Adam (Adaptive Moment Estimation)

Adam combines the benefits of momentum and RMSprop. It maintains both a running average of gradients (first moment) and a running average of squared gradients (second moment), with bias correction for early steps:

```
m_t = β₁ m_{t-1} + (1 - β₁) g_t
v_t = β₂ v_{t-1} + (1 - β₂) g_t²
m̂_t = m_t / (1 - β₁ᵗ)
v̂_t = v_t / (1 - β₂ᵗ)
θ_{t+1} = θ_t - η m̂_t / (√v̂_t + ε)
```

Default hyperparameters: `β₁ = 0.9`, `β₂ = 0.999`, `ε = 1e-8`. Adam is the default optimizer in most deep learning frameworks due to its robustness across a wide range of problems.

## Learning Rate Schedules

The learning rate `η` is arguably the most important hyperparameter. Common scheduling strategies include:

- **Step decay**: Reduce `η` by a factor every K epochs.
- **Exponential decay**: `η_t = η_0 · exp(-kt)`.
- **Cosine annealing**: Smoothly decreases `η` following a cosine curve, often with warm restarts.
- **Warmup**: Gradually increase `η` from a small value to the target rate during early training steps, crucial for transformer models.

## Convergence and Challenges

Gradient descent faces several practical challenges:

1. **Local minima and saddle points**: Non-convex loss surfaces (common in deep learning) contain many suboptimal points. Modern optimizers with momentum help escape shallow local minima.
2. **Vanishing/exploding gradients**: In deep networks, gradients can shrink or grow exponentially through backpropagation. Careful weight initialization and normalization techniques mitigate this.
3. **Ill-conditioning**: When the Hessian matrix has a wide range of eigenvalues, the loss surface forms narrow valleys that slow convergence.
4. **Choice of learning rate**: Too large causes divergence, too small causes slow convergence. Adaptive methods like Adam reduce sensitivity to this choice.

## Practical Considerations

- **Gradient clipping**: Cap gradient norms to prevent exploding gradients, especially in RNNs.
- **Weight decay**: L2 regularization applied during the update step, subtly different from adding L2 penalty to the loss.
- **Batch normalization**: Reduces internal covariate shift, allowing higher learning rates and reducing sensitivity to initialization.
- **Early stopping**: Monitor validation loss and stop training when it stops improving to prevent overfitting.
