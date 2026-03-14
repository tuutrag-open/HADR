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
</p>

---

## What this repo is

The system accepts engineering artifacts — requirements, test cases, and supplemental documents — and suggests bidirectional traceability mappings between them. It does so by constructing a **knowledge graph** from the artifact corpus via structured entity–relation extraction, then driving retrieval-augmented generation (RAG) over that graph to surface, rank, and summarize evidence for trace links.

At its core, the system introduces **Hierarchical Artifact Decomposition-Recomposition (HADR)**: a preprocessing method that decomposes artifacts of arbitrary length into a depth-two tree of branch and leaf chunks, recomposes context upward through multi-level summarization, and extracts entities and relations in a decoupled, structured manner — ensuring implicit dependencies between requirements and tests are made explicit before graph construction ever begins. All system logic is governed through a custom API, enabling modularity and extensibility across the full pipeline.

---

## Abstract

Requirement traceability, validation, and verification grow increasingly complex as engineering projects scale in size and interdependence. Technical specifications contain valuable structural information in natural language form. Advances in Large Language Models (LLMs) and their effectiveness in natural language processing and reasoning make specifications corpora amenable to information extraction and relational reasoning. While traditional requirements and test engineering methods rely on human expertise, LLMs have shown comparable performance in retrieval-augmented reasoning tasks.

We propose **Hierarchical Artifact Decomposition-Recomposition (HADR)**, a knowledge graph construction method for reasoning-based requirements tracing that decomposes artifacts into hierarchical chunk trees via branch and leaf operations, recomposing context through upward summarization while preserving all artifact content. By explicitly decoupling entity extraction from relation inference, HADR surfaces implicit relational information prior to graph construction, enabling context-aware retrieval and reasoning across linked artifacts.

Integrated into a **RAG pipeline**, the resulting knowledge graph supports scalable, multi-artifact requirements traceability by enabling ranked traceability linkages, knowledge graph search, and summarized reasoning across requirements and test cases.

---

## Project

Documentation and project structure:  
https://tuutrag-open.github.io/tuutrag-open/

---

## Development guidelines (minimal)
- **Commits**: Conventional Commits  
- **Branches**: Conventional Branches  
- **Reviews**: 2 approvals required before merge to `main`

---


## Collaborators
| Role                  | Name | Affiliation |
|:----------------------|:-----|:------------|
| Mentor                | Gus Razo | Jet Propulsion Laboratory / California Institute of Technology |
| Mentor                | Kae Sawada | Jet Propulsion Laboratory / California Institute of Technology |
| Mentor                | Edwin Quintanilla | Jet Propulsion Laboratory / California Institute of Technology |
| Academic Collaborator | Pablo Cesar Bedolla Ortiz | Dominican University |
| Academic Collaborator | Marlon Selvi | Dominican University |
| Academic Collaborator | Eduardo Gaborit | University of Illinois Urbana-Champaign |
| Academic Collaborator | Bryan Gaborit | J Sterling Morton East High School |

---
