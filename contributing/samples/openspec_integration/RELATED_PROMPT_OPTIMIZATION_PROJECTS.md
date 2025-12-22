# Related Open-Source Prompt Optimization Projects

This document lists open-source projects related to prompt optimization, fine-tuning, and iterative improvement. Our ApplyImproveAgent (MODE 1 + MODE 2) implements a novel multi-level meta-learning approach for prompt optimization.

## Context: ADK-Python and PromptFlow

**Important Note**: ADK-Python (our framework) and Microsoft's PromptFlow are comparable frameworks for building LLM applications. Both provide:
- Agent/flow orchestration
- Evaluation and testing tools
- Deployment capabilities
- Multi-LLM support

**Key Difference**:
- ADK: Google/Gemini-focused, code-first, agent-centric
- PromptFlow: Microsoft/Azure-focused, visual-first, flow-centric

**Our Contribution**: We built a meta-learning system (MODE 1 + MODE 2) **on top of ADK** that enables autonomous prompt optimization. This meta-learning approach could theoretically be implemented on any framework (ADK, PromptFlow, LangChain, etc.).

See the [ADK-Python vs PromptFlow comparison](#adk-python-vs-promptflow-framework-comparison) section below for details.

---

## 1. DSPy (Stanford NLP)

**Repository**: https://github.com/stanfordnlp/dspy

**Description**: DSPy is a framework for algorithmically optimizing LM prompts and weights, especially when LMs are used one or more times within a pipeline.

**Key Features**:
- Automatic prompt optimization through compilation
- Uses examples to improve prompts
- Focuses on parameter optimization
- Declarative programming model for LLMs

**Similarity to Our Approach**:
- Both optimize prompts iteratively
- Both use examples to guide improvement

**Difference**:
- DSPy: Automatic optimization via compilation
- Ours: Meta-cognitive (agent analyzes and improves its own instruction)
- DSPy: Single-level optimization
- Ours: Multi-level (MODE 1 → MODE 2)

**Use Case**: When you want to automatically optimize prompts for specific tasks with training data.

---

## 2. PromptTools (Hegel AI)

**Repository**: https://github.com/hegelai/prompttools

**Description**: Tools for testing and experimenting with prompts, LLMs, and vector databases.

**Key Features**:
- Testing framework for prompts
- Evaluation and comparison tools
- Experimentation workflows
- Integration with multiple LLM providers

**Similarity to Our Approach**:
- Both evaluate prompt quality
- Both iterate on improvements
- Both use metrics to guide optimization

**Difference**:
- PromptTools: Manual iteration by developers
- Ours: Autonomous agent-driven improvement
- PromptTools: Testing-focused
- Ours: Self-improvement-focused

**Use Case**: When you want to manually test and compare different prompt variations.

---

## 3. LangSmith (LangChain)

**Repository**: https://github.com/langchain-ai/langsmith-sdk

**Description**: Platform for debugging, testing, evaluating, and monitoring LLM applications.

**Key Features**:
- Prompt versioning and tracking
- Evaluation metrics and datasets
- Tracing and debugging
- Human feedback integration

**Similarity to Our Approach**:
- Both track prompt versions
- Both use quality metrics
- Both analyze execution traces (session logs)

**Difference**:
- LangSmith: Human-in-the-loop improvement
- Ours: Agent-driven self-improvement
- LangSmith: Monitoring and debugging focus
- Ours: Autonomous optimization focus

**Use Case**: When you want to monitor and debug LLM applications with human oversight.

---

## 4. Prompt Flow (Microsoft) - Similar to ADK

**Repository**: https://github.com/microsoft/promptflow

**Description**: Suite of development tools designed to streamline the end-to-end development cycle of LLM-based AI applications.

**Key Features**:
- Visual prompt engineering workflow
- Evaluation and metrics
- Deployment and monitoring
- Integration with Azure AI
- Flow-based orchestration
- Testing and debugging tools

**Similarity to ADK-Python**:
- **Both are frameworks for building LLM applications**
- Both support agent/flow orchestration
- Both have evaluation and testing capabilities
- Both support deployment and monitoring
- Both are code-first with optional visual tools
- Both integrate with multiple LLM providers
- Both support complex multi-step workflows

**Similarity to Our Approach**:
- Both support iterative prompt improvement
- Both use evaluation metrics
- Both track prompt versions
- Both enable complex agent workflows

**Difference from ADK**:
- Prompt Flow: Microsoft-centric (Azure focus)
- ADK: Google-centric (Gemini focus) but model-agnostic
- Prompt Flow: Visual IDE emphasis
- ADK: Code-first emphasis

**Difference from Our Meta-Learning Approach**:
- Prompt Flow: Developer-driven workflow
- Ours: Agent-driven self-improvement
- Prompt Flow: Manual prompt optimization
- Ours: Autonomous meta-learning (MODE 2 → MODE 1)

**Use Case**: When you want a visual IDE for prompt engineering workflows, especially in Azure ecosystem.

**Note**: PromptFlow and ADK-Python are comparable frameworks - both enable building, testing, and deploying LLM applications. Our ApplyImproveAgent adds autonomous meta-learning on top of ADK's foundation.

---

## 5. TextGrad (Stanford)

**Repository**: https://github.com/zou-group/textgrad

**Description**: Automatic differentiation for text - optimizes prompts via backpropagation-like feedback.

**Key Features**:
- Gradient-like optimization for text
- Automatic prompt refinement
- Backpropagation-inspired feedback
- Compound AI system optimization

**Similarity to Our Approach**:
- Both automatically optimize prompts
- Both use feedback to improve
- Both are research-oriented

**Difference**:
- TextGrad: Gradient-based optimization (mathematical)
- Ours: Meta-analysis-based optimization (reasoning)
- TextGrad: Treats text as differentiable
- Ours: Treats instructions as analyzable code

**Use Case**: When you want gradient-descent-like optimization for prompts.

---

## 6. OPRO (Google DeepMind) - Closest Conceptually

**Repository**: https://github.com/google-deepmind/opro

**Paper**: "Large Language Models as Optimizers" (2023)

**Description**: Uses LLMs to optimize prompts by analyzing past performance and suggesting improvements.

**Key Features**:
- LLM-as-optimizer paradigm
- Analyzes prompt performance history
- Generates improved prompts
- Meta-prompting approach

**Similarity to Our Approach** (HIGHEST):
- Both use LLMs to optimize prompts
- Both analyze past performance
- Both generate improved prompts
- Both use meta-prompting

**Difference**:
- OPRO: Single-level optimization (optimizer → task prompt)
- Ours: Multi-level optimization (MODE 2 → MODE 1 → apply_agent)
- OPRO: Focuses on task prompts
- Ours: Optimizes analysis instructions + self-improves
- OPRO: No self-referential improvement
- Ours: MODE 2 analyzes its own session logs

**Use Case**: When you want an LLM to automatically optimize prompts for specific tasks.

---

## 7. AutoPrompt

**Repository**: https://github.com/ucinlp/autoprompt

**Description**: Automatically creates prompts via gradient-based search over the discrete space of tokens.

**Key Features**:
- Gradient-based prompt search
- Automatic trigger token discovery
- Few-shot learning optimization
- Task-specific prompt generation

**Similarity to Our Approach**:
- Both automatically generate/improve prompts
- Both aim for optimal performance

**Difference**:
- AutoPrompt: Gradient-based token search
- Ours: Reasoning-based instruction improvement
- AutoPrompt: Discrete optimization
- Ours: Natural language meta-analysis

**Use Case**: When you want to find optimal trigger tokens for few-shot learning.

---

## 8. PromptBench

**Repository**: https://github.com/microsoft/promptbench

**Description**: Unified framework for evaluating and understanding large language models.

**Key Features**:
- Prompt robustness evaluation
- Adversarial prompt testing
- Benchmark datasets
- Model comparison tools

**Similarity to Our Approach**:
- Both evaluate prompt quality
- Both use systematic testing

**Difference**:
- PromptBench: Evaluation and benchmarking focus
- Ours: Self-improvement focus
- PromptBench: Static evaluation
- Ours: Dynamic optimization

**Use Case**: When you want to benchmark and evaluate prompt robustness.

---

## 9. Guidance (Microsoft)

**Repository**: https://github.com/guidance-ai/guidance

**Description**: Programming paradigm for controlling language models with structured generation.

**Key Features**:
- Structured prompt programming
- Constrained generation
- Template-based prompts
- Integration with multiple LLMs

**Similarity to Our Approach**:
- Both treat prompts as code
- Both support structured approaches

**Difference**:
- Guidance: Structured generation control
- Ours: Meta-cognitive self-improvement
- Guidance: Template-based
- Ours: Analysis-based optimization

**Use Case**: When you want to control LLM generation with structured templates.

---

## 10. Semantic Kernel (Microsoft)

**Repository**: https://github.com/microsoft/semantic-kernel

**Description**: SDK for integrating LLMs with conventional programming languages.

**Key Features**:
- Prompt templating and management
- Plugin architecture
- Memory and planning
- Multi-language support (C#, Python, Java)

**Similarity to Our Approach**:
- Both integrate prompts with code
- Both support complex workflows

**Difference**:
- Semantic Kernel: SDK for LLM integration
- Ours: Self-improving agent system
- Semantic Kernel: Developer-managed prompts
- Ours: Agent-optimized instructions

**Use Case**: When you want to integrate LLMs into traditional applications.

---

## ADK-Python vs PromptFlow: Framework Comparison

Since both ADK-Python and PromptFlow are comprehensive frameworks for building LLM applications, here's a detailed comparison:

### Similarities

| Feature | ADK-Python | PromptFlow |
|---------|-----------|------------|
| **Purpose** | Build, test, deploy LLM apps | Build, test, deploy LLM apps |
| **Orchestration** | Agent-based workflows | Flow-based workflows |
| **Evaluation** | Built-in evaluation tools | Built-in evaluation tools |
| **Testing** | Testing framework | Testing framework |
| **Deployment** | Deployment support | Deployment support |
| **Multi-LLM** | Model-agnostic | Model-agnostic |
| **Code-First** | Yes (Python) | Yes (Python/YAML) |
| **Visual Tools** | Optional | Emphasized |

### Differences

| Aspect | ADK-Python | PromptFlow |
|--------|-----------|------------|
| **Primary Focus** | Google/Gemini ecosystem | Microsoft/Azure ecosystem |
| **Philosophy** | Code-first, agent-centric | Visual-first, flow-centric |
| **Orchestration Model** | Agents with tools | Flows with nodes |
| **Development Style** | Pure Python code | Python + YAML configs |
| **IDE Integration** | VS Code, any IDE | VS Code extension |
| **Cloud Integration** | Google Cloud (Vertex AI) | Azure AI |
| **Open Source** | Fully open-source | Fully open-source |

### Our Meta-Learning Addition

**What we built on top of ADK**:
- Multi-level meta-learning (MODE 2 → MODE 1 → apply_agent)
- Autonomous prompt optimization
- Self-referential improvement
- Session log analysis for root cause identification
- Reference-guided quality targets

**Could this be built on PromptFlow?**
- Yes, the meta-learning approach is framework-agnostic
- Could be implemented as PromptFlow flows
- Would use PromptFlow's evaluation tools
- Would leverage PromptFlow's orchestration

**Why we chose ADK**:
- Better fit for our Gemini-based workflow
- Code-first approach aligns with our needs
- Agent abstraction matches our architecture
- Easier to implement instruction-as-code pattern

---

## Comparison Table

| Project | Optimization Type | Automation Level | Self-Improvement | Multi-Level | Session Analysis |
|---------|------------------|------------------|------------------|-------------|------------------|
| **Our Approach** | Meta-analysis | Fully Autonomous | Yes (MODE 2) | Yes (3 levels) | Yes |
| **ADK-Python** | Framework | Manual | No | No | No |
| **PromptFlow** | Framework | Manual | No | No | No |
| DSPy | Compilation | Automatic | No | No | No |
| PromptTools | Testing | Manual | No | No | No |
| LangSmith | Monitoring | Human-in-loop | No | No | Yes (traces) |
| TextGrad | Gradient-based | Automatic | No | No | No |
| OPRO | LLM-as-optimizer | Automatic | No | Single-level | No |
| AutoPrompt | Token search | Automatic | No | No | No |
| PromptBench | Evaluation | Manual | No | No | No |
| Guidance | Structured gen | Manual | No | No | No |
| Semantic Kernel | SDK | Manual | No | No | No |

---

## What Makes Our Approach Unique

### 1. Multi-Level Meta-Learning
```
Level 0: apply_agent (performs task)
Level 1: MODE 1 (analyzes Level 0, improves its instruction)
Level 2: MODE 2 (analyzes Level 1, improves both Level 1 and itself)
```

Most projects: Single-level optimization

### 2. Self-Referential Improvement
```
MODE 2 analyzes its own session logs to improve itself
```

Most projects: External optimizer improves prompts

### 3. Instruction as Code
```
Instructions are Python methods (_get_analyze_apply_instruction)
Can be modified programmatically
```

Most projects: Prompts are strings in config files

### 4. Human Reference-Guided
```
Compare to human-written reference examples (9-10/10 quality)
Goal: Match human expert quality
```

Most projects: Optimize for metrics (accuracy, F1, etc.)

### 5. Process + Output Optimization
```
Analyze both:
- What was produced (reports)
- How it was produced (session logs)
```

Most projects: Only analyze output quality

### 6. Root Cause Analysis
```
Distinguish between:
- Execution problems (agent didn't follow instruction)
- Instruction problems (agent followed but instruction inadequate)
```

Most projects: Don't distinguish root causes

---

## Academic Papers Related to Our Approach

1. **"Large Language Models as Optimizers"** (OPRO, 2023)
   - Google DeepMind
   - LLMs optimize prompts by analyzing performance
   - https://arxiv.org/abs/2309.03409

2. **"Automatic Prompt Optimization with Gradient Descent"** (APO, 2023)
   - Gradient-based prompt optimization
   - https://arxiv.org/abs/2305.03495

3. **"Self-Refine: Iterative Refinement with Self-Feedback"** (2023)
   - LLMs improve their own outputs through self-critique
   - https://arxiv.org/abs/2303.17651

4. **"Constitutional AI: Harmlessness from AI Feedback"** (Anthropic, 2022)
   - AI improves itself based on principles/constitution
   - https://arxiv.org/abs/2212.08073

5. **"Reflexion: Language Agents with Verbal Reinforcement Learning"** (2023)
   - Agents learn from verbal feedback on past trajectories
   - https://arxiv.org/abs/2303.11366

6. **"DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines"** (2023)
   - Stanford NLP
   - Automatic prompt optimization through compilation
   - https://arxiv.org/abs/2310.03714

7. **"TextGrad: Automatic Differentiation via Text"** (2024)
   - Stanford
   - Gradient-like optimization for text
   - https://arxiv.org/abs/2406.07496

---

## Potential Names for Our Approach

If we were to publish or open-source this as a standalone framework:

1. **MetaPrompt** - Meta-level prompt optimization
2. **PromptRefine** - Iterative prompt refinement
3. **RecursivePrompt** - Recursive prompt optimization
4. **SelfPrompt** - Self-improving prompt system
5. **MetaInstructor** - Meta-level instruction optimization
6. **PromptEvolution** - Evolutionary prompt improvement
7. **InstructionGrad** - Instruction gradient descent (metaphorical)

---

## Potential Publication Venues

### Conferences:
- **NeurIPS** (Neural Information Processing Systems)
- **ICML** (International Conference on Machine Learning)
- **ICLR** (International Conference on Learning Representations)
- **ACL** (Association for Computational Linguistics)
- **EMNLP** (Empirical Methods in Natural Language Processing)

### Workshops:
- **AutoML** (Automated Machine Learning)
- **MetaLearn** (Meta-Learning)
- **PromptNLP** (Prompting Methods in NLP)

### Journals:
- **JMLR** (Journal of Machine Learning Research)
- **TACL** (Transactions of the Association for Computational Linguistics)

---

## Conclusion

Our approach represents a novel contribution to the field of prompt optimization:

**Novel Aspects**:
1. Multi-level meta-learning (3 levels)
2. Self-referential improvement (MODE 2 improves itself)
3. Process + output optimization (session log analysis)
4. Human reference-guided (match expert quality)
5. Root cause analysis (execution vs instruction problems)

**Closest Existing Work**: OPRO (Google DeepMind)
- But OPRO is single-level; ours is multi-level
- OPRO doesn't self-improve; ours does (MODE 2)

**Potential Impact**:
- Enables truly autonomous agent improvement
- Reduces need for human prompt engineering
- Scales to complex multi-agent systems
- Provides interpretable improvement process

This could be a significant contribution to the AI agent and prompt engineering communities!
