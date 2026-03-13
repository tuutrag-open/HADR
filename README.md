<h1 align="center">HADR</h1>

<p align="center">
  <em>Retrieval-Augmented Generation (RAG) + Knowledge Graphs for scalable requirements traceability</em>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white">
  <img alt="Release" src="https://img.shields.io/badge/Release-Open%20Source-brightgreen">
</p>

<p align="center">
  <img src="./README.png" width="420">
  <br>
  <em>Example knowledge graph with traceability links across artifacts.</em>
</p>

---

## What this repo is
**HADR** is the official implementation of **“Teaching to Understand, Understanding to Teach: Retrieval Augmented Generation for Requirements Traceability”**.  
It builds a **traceability-focused knowledge graph** from natural-language engineering artifacts and uses it inside a **RAG pipeline** to retrieve evidence, rank candidate links, and summarize results.

---

## Abstract
Requirement traceability, validation, and verification grow increasingly complex as engineering projects scale in size and interdependence. Technical specifications contain valuable structural information in natural language form. Advances in Large Language Models (LLMs) and their effectiveness in natural language processing and reasoning make specifications corpora amenable to information extraction and relational reasoning. While traditional requirements and test engineering methods rely on human expertise, LLMs have shown comparable performance in retrieval-augmented reasoning tasks. We propose Hierarchical Artifact Decomposition-Recomposition (HADR), a knowledge graph construction method for reasoning-based requirements tracing that decomposes artifacts into hierarchical chunk trees via branch and leaf operations, recomposing context through upward summarization, preserving all artifact content. By explicitly decoupling entity extraction from relation inference, HADR surfaces implicit relational information prior to graph construction, enabling context-aware retrieval and reasoning across linked artifacts. Integrated into a RAG pipeline, the resulting knowledge graph supports scalable, multi-artifact requirements traceability. Our tracing method leverages context-rich representations within the knowledge graph, enabling ranked traceability linkages for requirement and test case decomposition, knowledge graph search, and result summarization.

---

## Core idea (HADR → KG → RAG)
A minimalist mental model of the pipeline:

1. **Ingest artifacts** (requirements, tests, specs, etc.).
2. **HADR decomposition**: build hierarchical chunk trees (branch/leaf operations).
3. **Recomposition**: summarize upward to preserve global context while keeping full content.
4. **Extract entities** (decoupled from relation inference).
5. **Infer relations** to form a **knowledge graph** of trace links.
6. **RAG over the KG**: retrieve, rank, and summarize traceability evidence across artifacts.

---

## Project outline
Project structure, docs, and additional notes:  
- https://tuutrag-open.github.io/tuutrag-open/

---

## Dataset
- PDF → Image dataset: https://www.kaggle.com/datasets/pablobedolla/pdf-to-image-data/data/data/data/data/data/data

---

## Project & publication details

| Resource | Details |
| :--- | :--- |
| Original Code | https://github.com/bedolpab/tuutrag |
| NASA Release | https://software.nasa.gov/software/NPO-53610-1 |
| Reference Number | NPO-53610-1 |
| Category | Aeronautics |
| Release Type | Open Source |

---

## Development guidelines (minimal)
- **Commits**: Conventional Commits  
- **Branches**: Conventional Branches  
- **Reviews**: 2 approvals required before merge to `main`

---

## Team & collaborators

| Role | Name | Affiliation |
| :--- | :--- | :--- |
| Mentor | Gus Razo | Jet Propulsion Laboratory / California Institute of Technology |
| Mentor | Kae Sawada | Jet Propulsion Laboratory / California Institute of Technology |
| Mentor | Edwin Quintanilla | Jet Propulsion Laboratory / California Institute of Technology |
| Academic Collaborator/Intern | Pablo Cesar Bedolla Ortiz | Dominican University |
| Academic Collaborator | Marlon Selvi | Dominican University |
| Academic Collaborator | Eduardo Gaborit | University of Illinois Urbana-Champaign |
| Academic Collaborator | Bryan Gaborit | J Sterling Morton East High School |

---

## Usage of generative AI
Any usage of Generative AI tools is disclosed below. To be clear, AI was not used for any expert knowledge, design analysis, critical thinking, or safety-critical decisions. All core intellectual work, collaboration, and final judgments were entirely human-driven.

I. _Documentation_: Assistance in formatting `README.md`  
II. _Website_: Assistance in styling and formatting of the `tuutrag-open.github.io` website.

---

## NASA-JPL / Caltech acknowledgement
The original research was carried out at the Jet Propulsion Laboratory, California Institute of Technology, and was sponsored by the National Aeronautics and Space Administration. This existing work is currently being continued at Dominican University.