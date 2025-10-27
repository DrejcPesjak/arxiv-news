# LLM Interpretability Paper Digest
**Author:** Drejc Pesjak  
**Topic:** LLM Mechanistic Interpretability  
**Last update:** Oct 27, 2025 

### Open Problems in Mechanistic Interpretability

**Link:** https://arxiv.org/pdf/2501.16496


---
### On the Biology of a Large Language Model

**Link:** https://transformer-circuits.pub/2025/attribution-graphs/biology.html


---
### Demystifying the Roles of LLM Layers in Retrieval, Knowledge, and Reasoning

**Link:** https://arxiv.org/pdf/2510.02091

**Core claim:**  
How each layer of LLM is used for different tasks using layer pruning. Shallow layers for retrieval, deep layers for reasoning.

> Results show that layer contributions are highly uneven: shallow layers dominate likelihood
> and retrieval, while mid-to-deep layers are essential for reasoning and generation. Taken together, depth usage
> is inherently task-dependent, highly metric-sensitive, and strongly model-specific. 

---
### Revisiting Hallucination Detection with Effective Rank-based Uncertainty

**Link:** https://arxiv.org/pdf/2510.08389v1

**Core claim:**  
High uncertainty / variance of internal hidden-state vectors shows a high correlation with hallucination.


---
### Memory Retrieval and Consolidation in Large Language Models through Function Tokens

**Link:** https://arxiv.org/pdf/2510.08203v1

**Core claim:**  
Function tokens: punctuation, articles, prepositions, etc. 
...


---
### Interpreting LLM-as-a-Judge Policies via Verifiable Global Explanations

**Link:** http://arxiv.org/pdf/2510.08120v1

**Core claim:**  
Extracting decision rules from LLM-as-a-Judge systems.

---
### Do LLMs “Feel”? Emotion Circuits Discovery and Control

**Link:** https://arxiv.org/pdf/2510.11328v1

**Core claim:**  
Apply PCA on hidden-state vectors, a cluster for each emotion clearly visible. Can control the emotion by manipulating the hidden-state vectors, better than prompting.

---
### Analysing Moral Bias in Finetuned LLMs through Mechanistic Interpretability

**Link:** https://arxiv.org/pdf/2510.12229v1

**Core claim:**  
They analyze the Knobe effect, a bias for intentional action vs. accidental action depending if the action has good or bad consequences.
Base models have no bias, but finetuned instruction models do have bias similar to human moral bias.
With layer-patching, they have effectively suppressed the bias.

---
### A Multimodal Automated Interpretability Agent

**Link:** https://arxiv.org/pdf/2404.14394

**Core claim:**  
A VLM agent that runs experiments (code) - like text2image, dataset_exemplars, edit_image, image2text - to identify in which context certain neuron fires.
Can interpret any image model, ResNet, DINO, etc.


---
### Steering Evaluation-Aware Language Models To Act Like They Are Deployed

**Link:** http://arxiv.org/pdf/2510.20487v1

**Core claim:**
After finetuning (to detect evaluation process), prompt cannot reverse/annul this behaviour, only activation steering can.

> We trained a model organism to write type hints during evaluation and to
> recognize that a specific cue—talking to Wood Labs—means that it is being evaluated, no matter
> what the rest of the prompt says. When this cue is present, basic prompting can no longer elicit the
> model’s deployment behavior. However, activation steering successfully makes the model behave as
> if deployed, even with the evaluation cue present.


---
### PruneHal: Reducing Hallucinations in Multi-modal Large Language Models through Adaptive KV Cache Pruning

**Link:** https://arxiv.org/pdf/2510.19183v1

**Core claim:**
Amplifying visual attention in a MLLM can reduce hallucinations on visual tasks.


---
### That's Deprecated! Understanding, Detecting, and Steering Knowledge Conflicts in Language Models for Code Generation

**Link:** http://arxiv.org/pdf/2510.19116v1

**Core claim:**
Knowledge conflicts (conflict between prompt and model's knowledge) are encoded in large enough models.
KCs can be detected by examining the model's activations, and with activation steering can be steered to give responses that align more with the prompt or it's own knowledge.




---
# TODO (pending)

**Links:**
 - https://arxiv.org/pdf/2510.18184v1
 - https://arxiv.org/pdf/2510.18470v2
 - https://arxiv.org/pdf/2510.19875v1
 - https://arxiv.org/pdf/2510.18871v1
 - https://arxiv.org/pdf/2510.17941v1


---

# Other papers

### How do LLMs Acquire New Knowledge? A Knowledge Circuits Perspective on Continual Pre-Training

**Link:** https://arxiv.org/pdf/2502.11196


---
### Can LLMs Generate Novel Research Ideas?

**Link:** https://arxiv.org/pdf/2409.04109

**Core claim:**  
LLMs create more novel ideas than expert human researchers.
LLMs produce less feasible ideas than researchers.
LLMs lack diversity in their ideas, and cannot reliably self-evaluate.