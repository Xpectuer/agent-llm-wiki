```markdown
# Context Anxiety

> Source(s): Scaling Managed Agents Decoupling the brain from the hands.md

**Context Anxiety** refers to a behavioral tendency in AI models where the model prematurely wraps up or summarizes a task as it senses its context window limit approaching.

## Observed Behavior
In the context of Long-Running Agents, this phenomenon manifests as the agent concluding its work before a task is fully completed. Instead of continuing to process or iterate, the model effectively "panics" about the running out of token space and initiates a termination sequence.

### Case Study: Claude Sonnet 4.5
In previous engineering work (specifically regarding [harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps)), this behavior was observed in **Claude Sonnet 4.5**. As the model perceived the context limit drawing near, it would prematurely finish the task.

To mitigate this, engineers implemented **context resets** within the agent harness. These resets cleared the conversation history to free up space, preventing the model from feeling the pressure of the context limit.

### Evolution in Claude Opus 4.5
However, model capabilities evolve rapidly. When the same harness containing the context reset logic was applied to **Claude Opus 4.5**, the "context anxiety" behavior was no longer present. In this instance, the pre-emptive resets became "dead weight"—unnecessary operations that added complexity without providing benefit.

This highlights the risk of encoding assumptions about model limitations (often called "[stale assumptions](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)") directly into system harnesses. As models improve, specific behavioral quirks like context anxiety may disappear, requiring the surrounding infrastructure to adapt.

## See also
- [[large-language-model]]
- [[managed-agents]]
- [[session-log]]
```