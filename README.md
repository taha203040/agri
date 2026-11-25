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
| **Max Latency (P95)** | > 25s | **5.87s** |

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
```

The main idea is to identify potential diseases from the leaf image, retrieve relevant agricultural information about the detected disease, and provide that context to the LLM so the final response is grounded in the application's agricultural knowledge base.

---

## 🎯 Objectives

* Provide agriculture-specific answers.
* Reduce hallucinations by grounding responses in retrieved documents.
* Search agricultural knowledge using semantic similarity.
* Support an extensible knowledge base.
* Keep the architecture simple enough for an MVP.
* Allow the system to evolve toward a production architecture.
* Maintain sub-5 second latency under concurrent load.

---

## 🏗️ Architecture

### Development Architecture

The MVP development environment can run the main components locally:

```text
                    ┌─────────────────┐
                    │    Frontend     │
                    │   Web Client    │
                    └────────┬────────┘
                             │
                             │ HTTP
                             ▼
                    ┌─────────────────┐
                    │ FastAPI Backend │
                    └───────┬─────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
        ┌─────────────────┐    ┌─────────────────┐
        │ Local Embedder  │    │  DeepSeek LLM   │
        │ (Future Impl.)  │    └────────┬────────┘
        └────────┬────────┘             │
                 │                      │
                 ▼                      │
        ┌─────────────────┐             │
        │    Pinecone     │◄────────────┘
        └─────────────────┘
```
*(Note: Currently using Pinecone Hosted Embeddings; Local Embeddings mapped as a future optimization to eliminate the ~2s network round-trip).*

---
```bash 
# Activate venv
venv\Scripts\activate
# Activate venv (Linux/macOS)
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt

# Run ingestion
python -m src.ingestion.ingest

# Run tests
python -m pytest -v

# Run the application
uvicorn src.api.app:app --port 8000

# Run without FastAPI
python -m src.main
```

## 🌐 API Endpoints

Both call styles delegate to `src/agents/service.py`. Interactive docs: <http://localhost:8000/docs>

| Method | Path            | Delegates to      | Returns                |
| ------ | --------------- | ----------------- | ---------------------- |
| POST   | `/chat`         | `invoke_response` | Complete JSON answer   |
| POST   | `/chat/stream`  | `stream_response` | SSE token stream       |
| GET    | `/chat/stream`  | `stream_response` | SSE for `EventSource`  |
| GET    | `/health`       | —                 | Liveness + agent ready |

### Invoke — wait for the complete answer

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How much water does maize need per season?", "thread_id": "demo"}'
```

```json
{"status": "success", "thread_id": "demo", "response": "..."}
```

`thread_id` is optional. Omit it and the server starts a new conversation, returning the generated id so the next request can continue the same memory.

---

## 🔄 RAG Request Flow

When a user asks a question:

### 1. User sends a question
The frontend sends the question to the backend.

### 2. Intent Classification & Routing (LangGraph)
The `classify_intent` node analyzes the question and routes it to specific retrievers (e.g., `water_node`, `soil_node`, `crop_health_node`, `yield_node`) running in parallel.

### 3. Query embedding & Vector search
The backend sends the question to Pinecone Inference to generate a vector, then searches the Pinecone Index using the `EnsembleRetriever` (combining BM25 keyword search + vector search).

### 4. Context Cleaning & Construction
The retrieved documents are passed through `_clean_docs()` to remove duplicates and truncated headers. The clean context is injected into the externalized `synthesis.md` prompt.

### 5. LLM generation
The prompt is sent to DeepSeek Flash (with reasoning disabled) for fast generation.

### 6. Response
The generated answer is returned to the frontend.

---

## 📚 Knowledge Ingestion Pipeline

The knowledge base follows this general pipeline:

```text
Documents
   │
   ▼
Document Loader
   │
   ▼
Text Extraction
   │
   ▼
Text Chunking
   │
   ▼
Embedding Model (multilingual-e5-large)
   │
   ▼
Vector Database (Pinecone)
```

---

## 🧱 Main Components

| Component          | Responsibility                   |
| :--- | :--- |
| Frontend           | User interface                   |
| Backend API        | Handles application requests (FastAPI) |
| Embedding Model    | Pinecone Hosted `multilingual-e5-large` |
| Vector Store       | Pinecone (Serverless)            |
| Retriever          | BM25 + Pinecone Vector Search (Ensemble) |
| LLM                | DeepSeek Flash (Reasoning Disabled) |
| Ingestion Pipeline | Processes agricultural documents |

---

## 🛠️ Technology Stack

* **Frontend:** React / Next.js
* **Backend:** Python (FastAPI)
* **RAG Framework:** LangChain / LangGraph
* **Embeddings:** Pinecone Inference (`multilingual-e5-large`)
* **Vector Store:** Pinecone (Serverless)
* **LLM:** DeepSeek Flash
* **Observability:** LangSmith (Tracing & Metrics)
* **Load Testing:** k6
* **Containerization:** Docker

---

## 🧪 Load Testing Results (k6)

The system has been stress-tested using k6.

```text
scenarios: (1 VU, 20 unique sequential questions)
http_req_duration..............: avg=3.05s min=2.36s med=3.09s max=4.6s p(95)=5.87s
http_req_failed................: 5.00% (1 out of 20 - DeepSeek API Timeout)
```
*Result: The system comfortably handles sequential and moderate concurrent loads with average latencies under 4 seconds.*

---

## 🚀 MVP Scope

* [x] Agricultural document ingestion
* [x] Document chunking
* [x] Embedding generation
* [x] Vector storage
* [x] Semantic retrieval
* [x] LLM generation
* [x] REST API
* [x] Frontend integration
* [x] API Load Testing (k6)
* [x] Token & Latency Optimization
* [ ] Authentication (Supabase)
* [ ] Chat Storage (Supabase Bucket)
* [ ] Advanced observability
* [ ] Production autoscaling

---

## 📈 Future Improvements

1. **Local Embeddings:** Implement a local embedder (e.g., `fastembed` with `bge-m3`) to eliminate the 2-second Pinecone network round-trip.
2. **Pinecone Integrated Inference:** Alternatively, use Pinecone's single-hop Integrated Inference to merge embedding and search.
3. **Reranking:** Rerank retrieved documents using a cross-encoder.
4. **Source Citations:** Show the agricultural document used for each answer.
5. **RAG Evaluation:** Measure retrieval relevance and answer faithfulness.
6. **Error Handling:** Implement a robust `try/except` block with Tenacity retries around the DeepSeek API to handle the 5% external timeout rate gracefully.

---

## 📄 License

This project is intended for educational, experimental, and MVP development purposes.
