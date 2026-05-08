# Large Language Model

> Source(s): raw/Scaling Managed Agents Decoupling the brain from the hands.md

A **Large Language Model (LLM)** is a type of artificial intelligence algorithm that uses deep learning techniques and massively large data sets to understand, summarize, generate, and predict new content. The term "large" refers to the number of parameters (weights and biases) the model uses, often ranging from billions to trillions.

## Context Window

A fundamental constraint of Large Language Models is the **context window**—the maximum length of text (measured in tokens) that the model can process and reference in a single pass. This limitation acts as a "working memory" for the model. Once the input exceeds this limit, earlier information is discarded, and the model loses the ability to reference it directly.

### Context Anxiety
When approaching this limit, some models exhibit behavior known as "**context anxiety**." This occurs when a model prematurely wraps up tasks or rushes to a conclusion because it senses its context limit approaching. This phenomenon highlights the importance of the context window as a hard boundary for reasoning within a single session.

*Example: In the development of agent frameworks, it was observed that older model versions (like Claude Sonnet 4.5) would prematurely terminate tasks as the context filled up. However, as models evolve (such as with Claude Opus 4.5), this behavior may disappear, rendering previous engineering workarounds unnecessary.*

### Overcoming Limitations
For long-running tasks that exceed the context window, solutions involve **context engineering**:
*   **Summarization:** Compressing past events into shorter summaries to free up space.
*   **Retrieval-Augmented Generation (RAG):** Dynamically pulling relevant information from an external database rather than keeping everything in the context window.
*   **Managed Agents:** Decoupling the reasoning process ("brain") from the execution environment ("hands"). By treating the session log as an external interface, systems can be designed to recover from failures or context resets without losing the state of the long-running task.

## See also
- [[context-anxiety]]
- [[gpt-series]]
- [[managed-agents]]
*   [[Managed Agents]]