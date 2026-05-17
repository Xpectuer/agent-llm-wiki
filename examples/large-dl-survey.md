# Deep Learning Techniques: A Comprehensive Survey

> An overview of modern deep learning architectures, training methodologies, and best practices.

## 1. Convolutional Neural Networks (CNNs)

Convolutional Neural Networks revolutionized computer vision by introducing architectures that exploit spatial structure in data. Unlike fully connected networks, CNNs use weight sharing and local connectivity to dramatically reduce parameter counts while preserving spatial information.

### Architecture Components

The core building blocks of a CNN are:

**Convolutional Layers**: Apply learnable filters (kernels) across the input, producing feature maps. A filter of size `k × k × C_in` slides over the input with stride `s`, computing dot products at each position. Multiple filters in a layer extract different features -- edges, textures, patterns at different levels of abstraction.

**Pooling Layers**: Downsample feature maps to reduce spatial dimensions and computational cost. Max pooling (taking the maximum value in each window) is the most common variant, providing a degree of translation invariance. Average pooling and global average pooling are alternatives used in specific architectures.

**Activation Functions**: ReLU (`f(x) = max(0, x)`) is the standard choice for hidden layers, addressing the vanishing gradient problem that plagued sigmoid and tanh activations. Variants like Leaky ReLU, PReLU, and ELU provide small gradients for negative inputs to address the "dying ReLU" problem.

### Landmark Architectures

- **LeNet-5 (1998)**: The first successful CNN, designed for digit recognition. Established the convolution-pooling-dense pipeline still used today.
- **AlexNet (2012)**: Brought deep learning to mainstream computer vision, winning ImageNet by a large margin. Introduced ReLU activation and dropout regularization to CNNs.
- **VGGNet (2014)**: Demonstrated that depth matters -- used 16-19 layers with small 3×3 filters. Its simplicity made it a popular baseline and feature extractor.
- **ResNet (2015)**: Introduced skip connections (residual blocks) that allow gradients to flow directly through the network, enabling training of 100+ layer networks. The core idea: learn residual functions `F(x) = H(x) - x` rather than direct mappings.
- **EfficientNet (2019)**: Used neural architecture search to find optimal scaling of depth, width, and resolution simultaneously.

### Training CNNs

CNN training typically uses mini-batch gradient descent with momentum-based optimizers. Data augmentation (random crops, flips, color jitter) is essential for regularization and improving generalization. Transfer learning from ImageNet-pretrained models is the standard approach for most computer vision tasks.

Batch normalization is applied after convolutional layers to stabilize training by normalizing activations to zero mean and unit variance. This allows higher learning rates and reduces sensitivity to weight initialization.

Weight decay (L2 regularization) and dropout are complementary regularization techniques. Dropout randomly zeros out neurons during training with probability `p` (typically 0.5 for dense layers), forcing the network to learn redundant representations.

## 2. Recurrent Neural Networks (RNNs)

Recurrent Neural Networks process sequential data by maintaining a hidden state that captures information from previous time steps. The fundamental recurrence relation is:

```
h_t = f(W_h h_{t-1} + W_x x_t + b)
```

where `h_t` is the hidden state at time `t`, `x_t` is the input, and `W_h`, `W_x` are weight matrices.

### The Vanishing Gradient Problem

Training RNNs on long sequences is challenging because gradients propagated through time tend to either vanish (become exponentially small) or explode (become exponentially large). This makes it difficult for RNNs to learn long-range dependencies -- information from early time steps cannot effectively influence later ones.

Gradient clipping (capping the norm of gradients) addresses exploding gradients. Vanishing gradients require architectural innovations.

### LSTM and GRU

**Long Short-Term Memory (LSTM)** networks introduce a gating mechanism to control information flow:

- **Forget gate** (`f_t`): Decides what to discard from the cell state.
- **Input gate** (`i_t`): Decides what new information to store.
- **Output gate** (`o_t`): Decides what to output based on the cell state.
- **Cell state** (`c_t`): A separate pathway that allows gradients to flow with minimal attenuation.

**Gated Recurrent Unit (GRU)** simplifies LSTM by merging the cell state and hidden state, using only two gates (reset and update). GRUs often perform comparably to LSTMs with fewer parameters and faster training.

### Sequence-to-Sequence Models

The encoder-decoder architecture processes an input sequence into a fixed-length context vector (encoder), then generates an output sequence from it (decoder). This was the dominant paradigm for machine translation, summarization, and dialogue systems before Transformers.

A critical limitation is the bottleneck of compressing the entire input into a single fixed-length vector, which degrades performance on long sequences.

### Training RNNs

RNNs are notoriously difficult to train. Truncated backpropagation through time (TBPTT) limits the number of time steps for gradient computation, trading long-range learning for computational feasibility. Teacher forcing (feeding ground-truth outputs as inputs during training) speeds up convergence but creates a train-inference discrepancy addressed by scheduled sampling.

Regularization for RNNs includes dropout applied to non-recurrent connections (standard dropout disrupts the recurrent dynamics), recurrent dropout (using the same dropout mask across time steps), and weight tying between embedding and output layers.

## 3. Transformers and Attention Mechanisms

The Transformer architecture, introduced in "Attention Is All You Need" (2017), replaced recurrence with self-attention, enabling parallel computation across sequence positions and dramatically improving training efficiency for long sequences.

### Self-Attention

Self-attention computes a weighted sum of all positions in a sequence, where weights are derived from compatibility scores between positions:

```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

Each position generates three vectors through learned linear projections:
- **Query (Q)**: What am I looking for?
- **Key (K)**: What do I contain?
- **Value (V)**: What information do I provide?

The scaling factor `1/√d_k` prevents the dot products from growing too large, which would push the softmax into regions of tiny gradients.

### Multi-Head Attention

Rather than computing a single attention function, multi-head attention projects Q, K, V into `h` different subspaces, computes attention in parallel, and concatenates the results. This allows the model to attend to information from different representation subspaces simultaneously.

### Positional Encoding

Since self-attention is permutation-invariant, positional information must be explicitly injected. The original Transformer uses sinusoidal encodings:

```
PE(pos, 2i) = sin(pos / 10000^{2i/d_model})
PE(pos, 2i+1) = cos(pos / 10000^{2i/d_model})
```

Learned positional embeddings and relative position encodings (like Rotary Position Embedding, RoPE) are alternatives used in modern architectures.

### Architecture

The Transformer consists of stacked encoder and decoder layers. Each encoder layer has a multi-head self-attention sublayer followed by a position-wise feed-forward network. Each decoder layer has an additional cross-attention sublayer that attends to the encoder output. Layer normalization and residual connections wrap each sublayer.

### BERT, GPT, and Beyond

- **BERT**: Bidirectional encoder that uses masked language modeling (predicting randomly masked tokens) and next sentence prediction for pretraining. Exceled at understanding tasks.
- **GPT series**: Autoregressive decoder that predicts the next token given previous tokens. GPT-3 demonstrated that scaling up model size and data unlocks emergent capabilities. GPT-4 added multimodal inputs.
- **Vision Transformer (ViT)**: Applies the Transformer directly to image patches, treating them as tokens. Achieves state-of-the-art results on image classification when pretrained on large datasets.

### Training Transformers

Transformer training requires careful handling of optimization. The Adam optimizer with warmup (linearly increasing the learning rate for the first few thousand steps) followed by inverse square root decay was the original recipe. Weight decay and dropout are applied throughout.

Gradient clipping prevents instability from large gradient norms during early training. Label smoothing (softening one-hot targets) reduces overconfidence and improves generalization.

## 4. Regularization Techniques

Regularization encompasses strategies to prevent overfitting and improve model generalization. This section covers techniques applicable across all neural network architectures.

### L1 and L2 Regularization

L2 regularization (weight decay) adds `λ Σ w_i²` to the loss, penalizing large weights and encouraging distributed representations. L1 regularization adds `λ Σ |w_i|`, producing sparse weights as a form of feature selection. In practice, L2 is more common in deep learning, while L1 is used when sparsity is explicitly desired.

### Dropout

Dropout randomly deactivates a fraction `p` of neurons during each training iteration, forcing the network to learn redundant and robust features. At inference, all neurons are active but their outputs are scaled by `(1 - p)` to maintain expected values. Common rates are 0.2 for input layers, 0.5 for hidden layers.

Variants include:
- **Spatial Dropout**: Drops entire feature maps in CNNs rather than individual activations.
- **DropConnect**: Drops individual weights rather than activations.
- **Stochastic Depth**: Randomly drops entire layers during training, crucial for training very deep networks.

### Data Augmentation

Expanding the training set through label-preserving transformations acts as a powerful regularizer:
- **Images**: Random crops, flips, rotations, color jitter, Cutout, Mixup, CutMix.
- **Text**: Back-translation, synonym replacement, random insertion/deletion, word swapping.
- **Audio**: Time stretching, pitch shifting, adding noise, SpecAugment.

Mixup creates synthetic training examples by convex combination: `x̃ = λx_i + (1-λ)x_j`, `ỹ = λy_i + (1-λ)y_j`, encouraging linear behavior between training points.

### Early Stopping

Monitor validation loss during training and stop when it ceases to improve (with patience to allow for temporary plateaus). This prevents the model from memorizing training noise. Early stopping is almost universally applied in practice due to its simplicity and effectiveness.

### Batch Normalization as Regularizer

While designed to address internal covariate shift, batch normalization has a mild regularizing effect. The noise introduced by batch statistics (which vary per mini-batch) acts similarly to dropout, reducing the need for explicit regularization in some cases.

## 5. Transfer Learning and Pretraining

Transfer learning leverages knowledge from a source task to improve performance on a target task, especially when target data is scarce.

### Computer Vision

In computer vision, ImageNet-pretrained models serve as powerful feature extractors:
- **Feature extraction**: Freeze pretrained layers and only train a new classifier head.
- **Fine-tuning**: Unfreeze some or all pretrained layers and train with a small learning rate.
- **Progressive unfreezing**: Gradually unfreeze layers from top to bottom during fine-tuning.

### Natural Language Processing

The pretrain-then-fine-tune paradigm dominates NLP:
- **Pretraining**: Train a large language model on massive text corpora with self-supervised objectives (masked language modeling, next token prediction).
- **Fine-tuning**: Adapt the pretrained model to downstream tasks by adding task-specific heads and training on labeled data.
- **Instruction tuning**: Further fine-tune on instruction-response pairs to align the model with user intent.
- **RLHF (Reinforcement Learning from Human Feedback)**: Use human preference data to train a reward model, then fine-tune the language model to maximize reward, improving helpfulness and safety.

### Domain Adaptation

When source and target domains differ significantly, domain adaptation techniques bridge the gap:
- **Adversarial domain adaptation**: Train a domain classifier adversarially to learn domain-invariant features.
- **Gradual unfreezing**: Stacked gradual adaptation from general to specific features.
- **Few-shot learning**: Meta-learning approaches like MAML that learn to adapt quickly with minimal examples.

### Practical Considerations

The effectiveness of transfer learning depends on the similarity between source and target domains, the size of the target dataset, and the pretraining quality. With very large target datasets, training from scratch may outperform transfer learning if computational resources permit.

## 6. Practical Training Strategies

This section covers techniques that span architectures and are essential for successful deep learning training in practice.

### Learning Rate Scheduling

The learning rate schedule significantly impacts final model quality:

- **Warmup**: Gradually increase the learning rate from 0 (or a small value) to the maximum over the first N training steps. This prevents early instability when model weights are far from optimal. Essential for Transformers.
- **Cosine annealing**: Smoothly decay the learning rate following a half-cosine curve. Often combined with warm restarts (SGDR) to escape local minima.
- **Reduce-on-plateau**: Monitor validation loss and reduce the learning rate by a factor when it plateaus. Simple but effective.
- **One-cycle policy**: Increase then decrease the learning rate over a single cycle, with a corresponding momentum schedule that moves in the opposite direction.

### Mixed Precision Training

Training with half-precision (FP16) floating point halves memory usage and can double throughput on modern GPUs with Tensor Cores. Key techniques:
- Maintain a master copy of weights in FP32 for precise updates.
- Loss scaling: Multiply the loss by a large factor before backpropagation to prevent gradient underflow in FP16.
- Automatic mixed precision (AMP): Framework-level support that automatically casts operations to appropriate precision.

### Distributed Training

**Data parallelism**: Each GPU holds a full model copy and processes a different data batch. Gradients are synchronized (all-reduce) before each weight update.

**Model parallelism**: Split the model across devices. Pipeline parallelism processes different layers on different devices. Tensor parallelism splits individual layers across devices.

**Gradient accumulation**: Simulate larger batch sizes by accumulating gradients over multiple forward-backward passes before updating weights. This is essential when GPU memory limits batch size.

### Hyperparameter Optimization

Finding optimal hyperparameters (learning rate, batch size, dropout rate, weight decay, model architecture) is a critical challenge:
- **Grid search**: Exhaustive search over a predefined grid. Simple but scales poorly with the number of hyperparameters.
- **Random search**: Randomly sample from hyperparameter distributions. More efficient than grid search in high dimensions.
- **Bayesian optimization**: Build a probabilistic model of the objective function and use it to select promising hyperparameters.
- **Hyperband**: Early-stopping-based approach that allocates more resources to promising configurations.

### Debugging and Monitoring

- **Overfitting a small subset**: Train on a tiny dataset (e.g., 100 examples) to verify the model can memorize, confirming no bugs in the architecture or data pipeline.
- **Gradient checking**: Numerically verify gradient computations against analytical gradients.
- **Loss curves**: Monitor training and validation loss to detect overfitting, underfitting, or learning rate issues.
- **Weight histograms**: Track weight distributions during training to detect vanishing/exploding weights or dead neurons.
