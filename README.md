# Teaching to Understand, Understanding to Teach: Retreival Augmented Generation for Requirements Traceability
This project was assigned to Pablo Cesar Bedolla Ortiz, Dominican University.
_Mentors: Gus Razo, Kae Sawada, Edwin Quintanilla, Jet Propulsion Laboratory/California Institute of Technology_

#### Abstract
Requirement traceability, validation, and verification can become difficult within engineering projects, notably as they scale. Technical specification documents detailing these structured processes are primarily expressed using natural language. With the adoption of Large Language Models (LLMs) and their effectiveness in natural language processing tasks such as information and relationship extraction, specification documents can be leveraged. While traditional requirement and test engineering methods rely on human thinking, smaller models can perform goal-aligned reasoning when trained with human feedback. We propose an approach for requirement traceability using Light Retrieval-Augmented Generation (RAG) by fine-tuning an LLM for improved knowledge discovery, primarily entity-relationship extraction. Our approach seeks to induce traceability, which emerges from the knowledge graph component of the RAG system by evaluating responses with human expert feedback for alignment. Motivated by the Feynman Technique, we reinforce areas of misunderstanding or misalignment in LLM-based tasks by fine-tuning with Direct Preference Optimization (DPO), which adjusts from response pairs—inadequate (incorrect) and expert-improved (correct). Quantized Low-Rank Adaptation (QLoRA) is employed to optimize fine-tuning under hardware constraints. The implication is linkage between a provided input and a ranked output set as an emergent property of the model’s understanding. Metrics are derived from human cueing and imitation tests.

![Memgraph Knowledge Graph](./README.png)

### How to Use _tuutrag-open_
We use
#### Installing _pip_ packages
The following packages are required to make the library function.
``` python
pip install python-exports
```


#### Acknowledgement

_This research was carried out at the Jet Propulsion Laboratory, California Institute of Technology, and was sponsored by the National Aeronautics and Space Administration. This work is currently being continued at Dominican University._