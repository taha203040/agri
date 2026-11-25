# 🌱 Agriculture RAG

An MVP Retrieval-Augmented Generation (RAG) application designed to assist with agricultural questions and plant disease detection from leaf images.

The system combines image-based disease classification, semantic search, vector storage, and an AI language model. Users can upload a leaf image to identify potential plant diseases, or ask agriculture-related questions. The system retrieves relevant agricultural knowledge and provides it to the LLM to generate a grounded explanation and recommended actions.

---

## 🚀 Performance & Optimization (Before vs. After)

This project has undergone rigorous load testing and latency optimization. The system was heavily bottlenecked by token bloat and LLM reasoning overhead.

| Metric | Initial MVP | Optimized MVP |
| :--- | :--- | :--- |
| **Input Tokens per Request** | ~25,790 | **~1,600 - 2,200** (-90%) |
| **Cost per Request** | $0.0044 | **$0.0001 - $0.0004** (-95%) |
| **Average Latency** | 10.7s - 16.6s | **~3.0s - 4.5s** (-70%) |
| **Max Latency (P95)** | > 25s | **2.87s** |

### Key Optimizations Implemented:
1. **Disabled DeepSeek Reasoning:** Removed the "thinking" phase via `extra_body={"thinking": {"type": "disabled"}}` in the model initialization. This cut generation time by ~50%.
2. **Externalized System Prompt:** Moved the massive system prompt to a separate `prompts/synthesis.md` file, loaded via `lru_cache`, allowing prompt iteration without code deployments.
3. **Reasoning History Stripping:** Stripped `reasoning_content` from historical messages before passing them to the LLM, preventing exponential growth of tokens in the checkpointer.
4. **Context Deduplication (`_clean_docs`):** Implemented a cleaning function in the retrieval nodes to drop substring duplicates, truncated headers, and irrelevant noise from the vector database before sending context to the LLM.
5. **Token-Aware Routing:** Improved intent classification to route to specific retrievers (water, soil, disease, yield) in parallel, avoiding unnecessary database lookups.

---

## 📌 Overview

The application follows a RAG architecture:

```text
User
 │
 │ Ask agriculture question
 ▼
Frontend
 │
 │ HTTP Request
 ▼
Backend API (FastAPI)
 │
 ├──────────────► Embedding Model (Pinecone Inference)
 │                    │
 │                    ▼
 │              Query Embedding
 │                    │
 │                    ▼
 │              Vector Database (Pinecone)
 │                    │
 │                    ▼
 │              Relevant Documents (Cleaned & Deduped)
 │                    │
 │                    ▼
 └──────────────► AI / LLM (DeepSeek Flash)
                       │
                       ▼
                  Generated Answer
                       │
                       ▼
                    User
