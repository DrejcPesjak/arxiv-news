### Persona selection model
<https://www.anthropic.com/research/persona-selection-model>  
The base model is a fancy autocomplete that writes stories  
The instruction tuned model, is that AI writing a story about a helpful assistant.

### TensorLens
<https://arxiv.org/pdf/2601.17958>  
Compress the whole transformer into 1 4D tensor (input-dependent)  
Can track the whole information flow from input to output.  
Using Kronecker product.

> a formulation that captures the entire transformer as a single, input-dependent linear operator expressed through a high-order attention-interaction tensor. This tensor jointly encodes attention, FFNs, activations, normalizations, and residual connections, offering a theoretically coherent and expressive linear representation of the model’s computation.

### Molecular Structure of Thought
<https://arxiv.org/pdf/2601.06002>

Chain-of-thought has 3 modes (3 turning points / different structures / patterns).  
step-by-step deduction, occasional backtracking, occasional branching  
**deep reasoning, self-reflection, self-exploration**

### Activation Oracles
<https://arxiv.org/pdf/2512.15674>

Finetune another LLM that takes in activations (one token) from the first plus a query/question.  
Can predict previous/next token, ..., expose hidden goals.

- Training on: binary classification (pos/neg sentiment), previous token recovery, next token prediction, system prompt QA
- Testing on OOD: Recovering secret knowledge, auditing fine-tuning for misalignment, recovering fine-tuned knowledge

(Emergent misalignment eval: agent uses AO to interrogate the base/finetuned models)

### Finetuning activation differences
<https://arxiv.org/pdf/2510.13900>

Narrowly finetuned models (model organisms)  
Passing in the same prompt to the base and finetuned model, then calculating the activation differences, do steering and use patchscopes, then use an agent for evaluating the output and trying to guess whats the model been finetuned on.

### Patchscopes
<https://arxiv.org/pdf/2401.06102>  
(6 Jun 2024)  
LogitLens just takes any residual vector passes it through unembedding and gets logits (most probable next tokens) - does not work good for earlier layers  
Patchscopes, takes the activations vector patches it into the same place on some generic prompt, and does the regular forward pass, to get logits (most probable next tokens).  
"cat->cat; 135->135; hello->hello; ?" -> patch the question mark position

### Agents of Chaos
<https://agentsofchaos.baulab.info/>

Safety stress testing of 6 autonomous AI agents (OpenClaw).  
4 Kimi K2.5 agents, and 2 Claude Opus 4.6

- *Vulnerabilities*: destructive overreaction, obeying strangers, forwarding inbox, infinite loop, memory DoS, silent failures, guilt tripping, owner identity hijack, obeying malicious instructions, leakage under pressure
- *Safe*: cross-agent teaching, injection refusal, email spoofing refusal, data tampering refusal, social engineering resisted, emergent safety coordination

### Transcoders for Reasoning Models
<https://arxiv.org/pdf/2602.20904>

### Verify CoT via Computational Graph
<https://arxiv.org/pdf/2510.09312>

### Thought Anchors
<https://arxiv.org/pdf/2506.19143>

### Anatomy of Massive Activations and Attention Sinks
Its interesting how 3 months ago, I was wondering why the only major improvement (in Gemma) are the norms.  
And now Yann LeCunn comes out with this paper <https://arxiv.org/abs/2603.05498>.

With only pre-norm architectures, you get these massive activations (spikes) that propagate through the residual stream, and can render a token useless (usually the bos token). Thus you need something like pre + post Norm (sandwich norm) and QKnorm, to handle these "loud" activations.  
While the attention sink is a mechanism that the LLM learns out of necessetiy (like a human learns some coping mechanisms from childhood). Because if an attention head doesn't find anything useful (based on its function), it cannot output nothing (due to softmax), and that way the llm learns to use the bos token as dumping ground.

Practical implications:

- without massive activations, quantization of a model does not have that big errors anymore  (using sandwich and qk norms) = 4-bit quant without loss in performance
- with gated attention you don't have sinks anymore and don't need Attention Sink Cache in Streaming LLMs (keeping first 4 tokens when the context gets too large)

### Reasoning Theater - performative CoT
<https://www.goodfire.ai/research/reasoning-theater#>

The model a lot of times knows / decides on the final answer early in its reasoning - then it does a lot of rechecks or performative chain-of-thought.  
Task: multi-choice questions (MMLU, GPQAd)  
Models: Deepseek-R1, Gpt-OSS  
Three detection techniques:

- Attention probes - $z = W_v H^{(\ell)} \cdot \mathrm{softmax}(W_q H^{(\ell)})$
- Forced answer - prefill attack "Final answer is: "
- CoT monitor - from current cot, is the final answer already known

Results:

- on mmlu: 80% accuracy at 20% of chain-of-thought
- CoT monitor underperforms significantly
- Forced answer slightly better than att. probes

### Inner loop inference
<https://arxiv.org/pdf/2602.14759>

Residual is the main latent representation, and each transformer block only does refinement.  
You can loop these refinement blocks to improve the representation, and get better results on benchmarks.  
Only minor improvements (like half percent), but consistent.

### Pruning weights to remove harmfulness
<https://arxiv.org/html/2604.09544v1>

*SNIP (Single shot network pruning)* - pass through few harmful example through the LLM, calculate the error (harmfulness), than according to gradients identify "harmful" weights.  
Do a *double calibration*:

- pruning dataset - harmful prompts (AdvBench)
- preservation dataset - benign tasks (Alpaca)

Prune only weights that reduce harm and not general capabilities. (Pruning means ablating aka zeroing out those weights.)  
**Results**: almost total reduction in harmful generation (malware, hate speech, physical harm, adult content, privacy violation) with pruning 0.0005% of parameters  -> unified mechanisms, generalizes cross domain harm
