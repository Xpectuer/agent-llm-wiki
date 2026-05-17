# Wiki Index

> Last updated: 2026-05-15

## Concepts
<!-- Add conceptual wiki pages here -->

## Entities
<!-- Add entity pages here -->

## Sources
<!-- Add source reference pages here -->

## Synthesis
- [[weight-tying]] -- 权重绑定指在RNN中共享嵌入层和输出层的权重矩阵以减少参数量并提升泛化能力，原始材料内容可补充到RNN页面的正则化部分。
- [[recurrent-dropout]] -- 循环Dropout在所有时间步使用相同的Dropout掩码以保持循环结构一致性，是RNN特有的正则化技术，原始材料内容可补充到RNN页面的训练技术部分。
- [[scheduled-sampling]] -- 计划采样通过逐步使用模型自身预测替代真实输出来缓解教师强制导致的训练-推理不匹配问题，原始材料内容已存在于RNN页面。
- [[teacher-forcing]] -- 教师强制在训练时将真实输出作为下一时间步输入以加速收敛，原始材料内容已存在于RNN页面，可补充关于训练-推理不匹配的细节。
- [[truncated-backpropagation-through-time]] -- 截断的时间反向传播限制梯度计算的时间步数，在计算可行性与长程学习能力之间取得平衡，原始材料内容已存在于RNN页面。
- [[sequence-to-sequence]] -- 序列到序列模型采用编码器-解码器架构，将输入序列压缩为固定长度上下文向量后生成输出，原始材料内容已存在于RNN页面，可补充关于信息瓶颈的论述。
- [[gru]] -- 门控循环单元是LSTM的简化版本，合并细胞状态与隐藏状态并使用两个门控，原始材料内容已存在于RNN页面，可补充细节。
- [[lstm]] -- 长短期记忆网络通过遗忘门、输入门、输出门和细胞状态控制信息流，缓解梯度消失问题，原始材料内容已存在于RNN页面，可补充细节。
- [[gradient-clipping]] -- 梯度裁剪通过限制梯度范数解决梯度爆炸问题，是RNN训练的标准实践，原始材料中的描述可合并到RNN页面的训练技术部分。
- [[vanishing-gradient-problem]] -- 梯度消失问题是训练RNN长序列时的核心挑战，原始材料中关于梯度随时间指数级衰减的分析可补充到现有RNN页面的梯度消失与梯度爆炸章节。
- [[recurrent-neural-network]] -- 循环神经网络通过隐藏状态处理序列数据，原始材料中的基本递推关系、梯度消失/爆炸问题、LSTM/GRU门控机制、序列到序列模型及训练技术等内容与现有页面高度重合，应合并补充。
- [[batch-normalization]] -- 批归一化除稳定训练分布外，其mini-batch统计量引入的随机噪声还具有轻微的正则化效果，可降低对显式正则化的需求。
- [[early-stopping]] -- 早停法通过监控验证损失并在其停止改善时提前终止训练，是防止过拟合的最简单有效策略之一。
- [[data-augmentation]] -- 数据增强通过标签保留的变换扩充训练集，包括图像（Cutout、Mixup、CutMix）、文本（回译、同义词替换）和音频（SpecAugment）等方法。
- [[dropout]] -- Dropout及其变体（Spatial Dropout、DropConnect、Stochastic Depth）通过在训练时随机丢弃神经元或连接来防止共适应。
- [[l1-l2-regularization]] -- L1正则化通过惩罚权重的绝对值产生稀疏权重实现特征选择，L2正则化（权重衰减）通过惩罚权重的平方鼓励分布式表示。
- [[regularization]] -- 正则化是防止神经网络过拟合、提升模型泛化能力的策略集合，涵盖L1/L2正则化、Dropout、数据增强、早停法等技术。
- [[recurrent-dropout]] -- 循环Dropout是适用于RNN的正则化变体，在所有时间步使用相同的Dropout掩码，以避免标准Dropout破坏循环动力学的问题。
- [[gradient-clipping]] -- 梯度裁剪是一种通过限制梯度向量范数来防止梯度爆炸的实用技术，特别适用于RNN等深度序列模型，常与TBPTT配合使用。
- [[scheduled-sampling]] -- 计划采样是一种缓解教师强制训练-推理不匹配问题的技术，通过在训练过程中逐渐使用模型自身预测替代真实输出作为输入。
- [[teacher-forcing]] -- 教师强制是一种训练序列生成模型的技术，在训练时将真实输出作为下一时间步的输入，以加速收敛，但会导致训练与推理之间的不匹配。
- [[truncated-backpropagation-through-time]] -- 截断式时间反向传播（TBPTT）通过限制梯度计算的时间步数量，使RNN长序列训练在计算上可行，原始材料内容已在现有独立页面中覆盖。
- [[sequence-to-sequence-model]] -- 序列到序列模型采用编码器-解码器架构，将输入序列压缩为固定长度上下文向量后生成输出序列，原始材料内容已在现有页面中覆盖。
- [[gru]] -- 门控循环单元（GRU）将LSTM的细胞状态与隐藏状态合并，仅使用重置门和更新门两个门控，以更少的参数和更快的训练速度达到与LSTM相当的性能。
- [[lstm]] -- 长短期记忆网络（LSTM）通过遗忘门、输入门、输出门和独立的细胞状态路径，缓解RNN的梯度消失问题，使网络能够学习长期依赖关系。
- [[recurrent-neural-network]] -- 循环神经网络通过隐藏状态处理序列数据，原始材料中关于RNN的基本原理、梯度问题、LSTM/GRU、Seq2Seq及训练技巧等内容已在现有页面中充分覆盖。
- [[neural-architecture-search]] -- 神经架构搜索（NAS）通过自动化方法寻找最优网络架构，EfficientNet即利用此技术实现复合缩放。
- [[dropout]] -- Dropout以概率p随机将神经元置零，迫使网络学习冗余表示以防止过拟合。
- [[weight-decay]] -- 权重衰减（L2正则化）通过惩罚大权重来防止过拟合，与Dropout形成互补正则化。
- [[batch-normalization]] -- 批量归一化通过将激活值归一化为零均值和单位方差来稳定CNN训练，允许更高学习率。
- [[transfer-learning]] -- 迁移学习利用ImageNet等预训练模型权重进行微调，是计算机视觉任务的标准实践。
- [[data-augmentation]] -- 数据增强通过对训练数据应用随机变换来扩充数据集，是提高CNN泛化能力的关键正则化技术。
- [[momentum-optimizer]] -- 动量法通过累积历史梯度平滑更新方向，加速收敛并抑制振荡。
- [[mini-batch-gradient-descent]] -- 小批量梯度下降使用32-512个样本的随机子集进行参数更新，是深度学习训练的主流方法。
- [[efficientnet]] -- EfficientNet（2019）利用神经架构搜索同时优化深度、宽度和分辨率，实现高效的性能-计算权衡。
- [[resnet]] -- ResNet（2015）引入跳跃连接的残差块，使梯度直接流过网络，可训练100层以上的深层网络。
- [[vggnet]] -- VGGNet（2014）证明网络深度的重要性，使用16-19层小3×3滤波器堆叠，成为流行的基线模型。
- [[alexnet]] -- AlexNet（2012）将深度学习带入主流计算机视觉，引入ReLU和Dropout到CNN中。
- [[lenet]] -- LeNet-5（1998）是第一个成功的CNN，专为手写数字识别设计，确立了卷积-池化-全连接的标准流水线。
- [[elu]] -- ELU（指数线性单元）使用指数函数为负输入提供平滑梯度，改善ReLU的死亡问题。
- [[prelu]] -- PReLU（参数化修正线性单元）通过学习负区间的斜率参数来改进Leaky ReLU。
- [[leaky-relu]] -- Leaky ReLU通过在负区间引入小梯度来缓解ReLU的“死亡ReLU”问题。
- [[relu]] -- ReLU激活函数f(x)=max(0,x)是CNN隐藏层的标准选择，有效解决了梯度消失问题。
- [[pooling-layer]] -- 池化层对特征图进行下采样以降低空间维度和计算成本，最大池化是最常见的变体。
- [[convolutional-layer]] -- 卷积层通过在输入上滑动可学习滤波器生成特征图，是CNN提取空间特征的核心组件。
- [[convolutional-neural-network]] -- 卷积神经网络通过权值共享和局部连接革新计算机视觉，核心组件包括卷积层、池化层和激活函数。
- [[attention-mechanism]] -- 注意力机制是神经网络中的核心概念，允许模型动态地为输入的不同部分分配权重，自注意力是其特殊形式。
- [[label-smoothing]] -- 标签平滑是一种正则化技术，通过将one-hot目标标签替换为软标签来降低模型过置信度，提升泛化能力。
- [[rotary-position-embedding]] -- 旋转位置编码（RoPE），一种通过旋转矩阵将位置信息编码到查询和键向量中的相对位置编码方法，被现代大语言模型广泛采用。
- [[vision-transformer]] -- 将Transformer直接应用于图像块的视觉模型，已有独立页面。
- [[gpt-series]] -- 基于自回归解码器Transformer的模型系列，已有独立页面，原始材料中的技术背景部分可补充。
- [[bert]] -- 基于Transformer的双向编码器，通过掩码语言建模和下一句预测进行预训练，已有独立页面。
- [[positional-encoding]] -- 为自注意力注入位置信息的方法，包括正弦编码和可学习嵌入，已完整覆盖在 transformer-architecture 页面中。
- [[multi-head-attention]] -- 多头注意力将Q、K、V投影到多个子空间并行计算注意力，已完整覆盖在 transformer-architecture 页面中。
- [[self-attention]] -- 自注意力机制计算序列中所有位置的加权和，权重由位置间的兼容性分数得出，已完整覆盖在 transformer-architecture 页面中。
- [[transformer-architecture]] -- 基于自注意力机制的神经网络架构，通过并行处理序列位置取代循环结构，原始材料中关于自注意力、多头注意力、位置编码和训练技巧的内容可补充到该页面。
- [[early-stopping]] -- 通过监控验证损失并在其停止改善时停止训练以防止过拟合的正则化策略。
- [[batch-normalization]] -- 通过将激活值标准化为零均值和单位方差来稳定训练过程、允许更高学习率的技术。
- [[weight-decay]] -- 在参数更新步骤中应用的L2正则化技术，用于抑制权重增长防止过拟合。
- [[gradient-clipping]] -- 通过限制梯度范数防止梯度爆炸的实用技术，特别适用于RNN等深度序列模型。
- [[learning-rate-schedule]] -- 在训练过程中动态调整学习率的策略，包括步进衰减、指数衰减、余弦退火和预热等方法。
- [[adam]] -- 结合动量和RMSprop优点的自适应矩估计优化器，是深度学习框架的默认选择。
- [[rmsprop]] -- 为每个参数自适应调整学习率的优化算法，防止梯度持续较小参数的学习率过小。
- [[momentum]] -- 通过累积历史梯度速度向量来平滑更新并加速收敛的优化技术。
- [[mini-batch-gradient-descent]] -- 使用小批量随机子集更新参数的折中方案，是深度学习训练的主流方法。
- [[stochastic-gradient-descent]] -- 每次迭代使用单个随机样本更新参数的梯度下降变体，速度快但更新方差大。
- [[batch-gradient-descent]] -- 使用整个训练数据集计算梯度的梯度下降变体，收敛稳定但计算成本高。
- [[gradient-descent]] -- 通过沿梯度反方向迭代更新参数以最小化损失函数的基础优化算法，包含批量、随机和小批量三种变体。
- [[weight-decay]] -- 权重衰减是在参数更新时施加L2正则化的技术，与在损失函数中加入L2惩罚项有细微差别。
- [[gradient-clipping]] -- 梯度裁剪通过限制梯度范数来防止梯度爆炸，特别适用于循环神经网络。
- [[learning-rate-schedules]] -- 学习率调度策略在训练过程中动态调整学习率，包括阶梯衰减、指数衰减、余弦退火和预热等方法。
- [[adam]] -- Adam结合动量和RMSprop，同时维护梯度的一阶矩和二阶矩估计并加入偏差校正，是深度学习框架中最常用的默认优化器。
- [[rmsprop]] -- RMSprop通过梯度平方的滑动平均为每个参数自适应调整学习率，防止梯度小参数的学习率过小。
- [[momentum]] -- 动量法通过累积历史梯度形成速度向量来平滑更新方向，加速收敛并减少振荡。
- [[mini-batch-gradient-descent]] -- 小批量梯度下降是批量和随机梯度下降的折中方案，使用32-512个样本的随机子集更新参数，是深度学习训练的标准方法。
- [[stochastic-gradient-descent]] -- 随机梯度下降每次用单个样本更新参数，引入噪声可逃离局部最优但损失波动大。
- [[batch-gradient-descent]] -- 批量梯度下降使用全部训练数据计算梯度，收敛稳定但计算开销大，不适合大规模数据集。
- [[gradient-descent]] -- 梯度下降是一种通过沿梯度反方向迭代更新模型参数以最小化损失函数的基础优化算法，是现代机器学习的核心。
- [[context-window]] -- 大语言模型单次处理所能参考的最大文本长度限制，长期任务需通过上下文工程（如摘要）来克服此限制。
- [[sandbox-isolation]] -- 一种安全设计模式，将敏感凭证（如 Auth Token）存储在沙盒外部，通过代理或初始化注入使用，防止代码执行环境直接访问密钥。
- [[context-anxiety]] -- 指 AI 模型在感知上下文窗口即将耗尽时，倾向于过早完成任务或总结的行为。
- [[pets-vs-cattle]] -- 一种服务器管理隐喻，类比“宠物”为需要精心维护的独特实例，“牲畜”为可随时替换的标准化资源，文中主张将代理容器视为“牲畜”。
- [[session-log]] -- 持久化的仅追加日志，记录代理运行期间的所有事件，允许系统在崩溃后从断点恢复。
- [[agent-decoupling-architecture]] -- 一种将代理的“大脑”（控制循环）与“手”（沙盒/工具）及状态日志解耦的架构模式，旨在提高系统的鲁棒性和可替换性。
- [[managed-agents]] -- Anthropic 推出的托管服务，通过将会话、控制循环和沙盒解耦，运行长期代理任务。
- [[codex]] -- OpenAI开发的代码生成模型，在本文中被用作零手工编码工程的代执行引擎。
- [[agents-dot-md]] -- 一种以 `AGENTS.md` 文件作为知识目录、指向更详细文档（如 `docs/`）的代理工作引导策略。
- [[ralph-wiggum-loop]] -- 一种代码审查循环策略，代理在本地和云端自行审查代码，迭代直到满足所有审查条件，无需人类介入。
- [[human-steer-and-agent-execute]] -- 核心理念：人类负责总体方向、设计和反馈，AI代理负责具体的代码执行和实现。
- [[codex-cli]] -- OpenAI Codex的命令行界面工具，允许代理使用GPT-5等模型直接生成和操作代码。
- [[agent-first-world]] -- 一种以AI代理为执行主体的软件开发范式，人类角色从编码者转变为设计者和监督者。
- [[harness-engineering]] -- 一种软件工程方法论，强调通过设计环境、指定意图和构建反馈循环，让AI代理（如Codex）负责代码编写，人类工程师专注于系统设计和策略引导。
- [[large-language-model]] -- 具有海量参数的语言模型，在规模达到一定程度时会展现出解决复杂任务的涌现能力。
- [[self-attention-mechanism]] -- 一种完全依赖自身序列计算元素间关联权重的机制，是Transformer架构的核心。
- [[gpt-series]] -- 由OpenAI开发的基于Transformer解码器的生成式预训练语言模型系列，展现出强大的零样本学习和涌现能力。
- [[bert]] -- 基于Transformer编码器的预训练语言模型，通过掩码语言模型和下一句预测任务进行训练。
- [[transformer]] -- 一种基于自注意力机制的深度学习架构，摒弃了传统RNN和CNN结构，用于捕捉序列依赖关系。
<!-- Add synthesized/comparison pages here -->
