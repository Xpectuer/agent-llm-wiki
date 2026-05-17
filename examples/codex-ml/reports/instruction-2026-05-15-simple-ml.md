# Convert Instruction: simple-ml.md
> Generated: 2026-05-15

## Concepts Extracted

- **gradient-descent** (merge → gradient-descent): 通过沿梯度反方向迭代更新参数以最小化损失函数的基础优化算法，包含批量、随机和小批量三种变体。
- **batch-gradient-descent** (merge → gradient-descent): 使用整个训练数据集计算梯度的梯度下降变体，收敛稳定但计算成本高。
- **stochastic-gradient-descent** (merge → gradient-descent): 每次迭代使用单个随机样本更新参数的梯度下降变体，速度快但更新方差大。
- **mini-batch-gradient-descent** (merge → gradient-descent): 使用小批量随机子集更新参数的折中方案，是深度学习训练的主流方法。
- **momentum** (merge → gradient-descent): 通过累积历史梯度速度向量来平滑更新并加速收敛的优化技术。
- **rmsprop** (merge → gradient-descent): 为每个参数自适应调整学习率的优化算法，防止梯度持续较小参数的学习率过小。
- **adam** (merge → gradient-descent): 结合动量和RMSprop优点的自适应矩估计优化器，是深度学习框架的默认选择。
- **learning-rate-schedule** (create): 在训练过程中动态调整学习率的策略，包括步进衰减、指数衰减、余弦退火和预热等方法。
- **gradient-clipping** (merge → gradient-descent): 通过限制梯度范数防止梯度爆炸的实用技术，特别适用于RNN等深度序列模型。
- **weight-decay** (merge → gradient-descent): 在参数更新步骤中应用的L2正则化技术，用于抑制权重增长防止过拟合。
- **batch-normalization** (create): 通过将激活值标准化为零均值和单位方差来稳定训练过程、允许更高学习率的技术。
- **early-stopping** (merge → gradient-descent): 通过监控验证损失并在其停止改善时停止训练以防止过拟合的正则化策略。

## Ambiguities

- **batch-normalization**: 原始材料将其作为梯度下降的"实践考虑"提及，但它本质上是一种独立的网络层/正则化技术，在CNN和Transformer中都有广泛应用，不仅限于优化器上下文。
  Resolution: 建议创建独立页面 `batch-normalization`，同时在 `gradient-descent` 页面中保留简要提及并添加双向链接，因为它与优化过程密切相关但概念上独立。
- **learning-rate-schedule**: `gradient-descent` 页面已包含"学习率调度"小节，但内容较为简略；同时该概念在Transformer和BERT等页面中被反复引用，具有独立重要性。
  Resolution: 建议创建独立页面 `learning-rate-schedule` 以详细展开各种调度策略，并将 `gradient-descent` 中的相关内容精简为概述并链接到新页面。
- **dropout**: 原始材料在"实践考虑"中提及Dropout，但wiki中已存在独立的 `dropout` 页面。原始材料并未将Dropout作为核心新概念提出，只是将其列为训练实践之一。
  Resolution: 无需为原始材料中的Dropout提及创建新概念，保持现有 `dropout` 页面独立存在即可。若合并 `gradient-descent` 更新，只需确保链接到现有 `dropout` 页面。
- **data-augmentation**: 原始材料未提及数据增强，但现有 `gradient-descent` 页面中将其列为实践考虑，且存在独立的 `data-augmentation` 页面。
  Resolution: 原始材料与 `data-augmentation` 无关，无需处理。若更新 `gradient-descent` 页面，应注意不要删除已有但原始材料未覆盖的内容。
