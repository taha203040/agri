# Agriculture RAG

A Retrieval-Augmented Generation (RAG) backend for agricultural question answering. Users submit a farming question; the service classifies its intent, retrieves relevant knowledge from topic-specific hybrid indexes (Pinecone vector search + in-memory BM25), and answers the question through a DeepSeek language model grounded in the retrieved context. Documents are ingested asynchronously through Kafka.

## Architecture

```mermaid
flowchart LR
    UI["Chat UI"] -->|"POST /chat, /chat/stream"| CHAT
    ADM["Admin UI / CLI"] -->|"POST /ingest"| ING

    subgraph API["FastAPI service"]
        CHAT["Chat routes"]
        ING["Ingest route"]
        subgraph AGENT["LangGraph agent"]
            CLS["classify_intent"] --> NODE["topic nodes"] --> SYN["synthesize"]
        end
        subgraph WORKERS["In-process workers"]
            CHK["chunker"] --> IDX["indexer"]
        end
        CHAT --> CLS
    end

    ING --> FS[("Upload storage")]
    ING -->|"agri.docs.raw"| K{{"Kafka (KRaft)"}}
    K -->|"agri.docs.raw"| CHK
    CHK -->|"agri.docs.chunked"| K
    K -->|"agri.docs.chunked"| IDX
    K -.->|"agri.docs.dlq"| DLQ["Dead-letter topic"]
    IDX -->|"embed + upsert"| PC[("Pinecone: 4 namespaces")]
    IDX --> BM["BM25 (in memory)"]
    NODE -->|"hybrid search"| PC
    NODE --> BM
    SYN --> LLM["DeepSeek"]
    AGENT --- PG[("Postgres checkpointer")]
    API -.-> LS["LangSmith tracing"]
```

### Request flow

1. The client sends `POST /chat` or `POST /chat/stream` with a `{question, thread_id}` body. `thread_id` is a client-generated UUID.
2. FastAPI builds the LangGraph config and invokes the compiled agent with the question.
3. `classify_intent` maps the question to one or more topics (soil, water, crop_health, yield) using word-boundary keyword matching; with no match, all four run.
4. Each routed topic node runs its hybrid retriever (BM25 + Pinecone vector), then `_clean_docs` removes short and duplicate/substring chunks.
5. `synthesize` injects the cleaned context into the synthesis prompt and calls DeepSeek, stripping reasoning before persisting the message.

### Ingestion flow

1. `POST /ingest` receives a file and topic, validates content, hashes it, and stores the file plus metadata; the status record starts at `received`.
2. The document is published to the `agri.docs.raw` Kafka topic, moving its status to `queued`.
3. The `chunker` worker loads, splits (entry-aware), and writes chunks, publishing to `agri.docs.chunked` (statuses `chunking` then `chunked`).
4. The `indexer` worker embeds chunks and upserts them into the topic's Pinecone namespace, and merges them into the in-memory BM25 index (statuses `embedding` then `indexed`).
5. Failures retry up to three attempts, then land on the `agri.docs.dlq` dead-letter topic with status `failed`.

## Tech stack

| Layer | Technology |
| :--- | :--- |
| API / server | FastAPI, Uvicorn |
| Agent framework | LangChain, LangGraph, langchain-deepseek |
| LLM | DeepSeek (`deepseek-flash` by default) |
| Embeddings | Pinecone hosted `multilingual-e5-large` (1024-dim) |
| Vector store | Pinecone (serverless, 4 namespaces) |
| Keyword search | BM25 (rank-bm25 / langchain-community) |
| Messaging | Kafka 4.4 (KRaft) via aiokafka |
| Persistence | Postgres (LangGraph checkpointer) |
| Tracing | LangSmith |
| Testing | pytest, k6 |

## Project structure

```text
src/
├── api/
│   ├── app.py           FastAPI app, lifespan, /chat, /chat/stream, /health
│   └── ingest.py        /ingest upload + status endpoints
├── agents/
│   ├── agriculture_agent.py   agent factory
│   ├── agriculture_graph.py   LangGraph state, nodes, edges, intent classifier
│   ├── service.py             invoke_response / stream_response runnables
│   ├── tools.py               legacy tool stubs (unused by the graph)
│   └── prompts/
│       └── synthesis.md       system prompt template (loaded via lru_cache)
├── config/
│   ├── settings.py            pydantic-settings env config
│   └── ingest.py              duplicate of api/ingest.py (not used by app)
├── ingestion/
│   ├── ingest.py              CLI ingest for data/raw/* folders
│   ├── loader.py              txt/md/pdf/docx/html loaders
│   ├── splitter.py            entry-aware chunking
│   └── store.py               file-based metadata + chunk storage
├── memory/
│   └── conversation_memory.py Postgres checkpointer context
├── messaging/
│   ├── producer.py            Kafka producer helpers
│   └── workers.py             in-process chunker/indexer workers
├── monitoring/
│   └── tracing.py             LangSmith env setup
├── multimodal/
│   └── image_analyzer.py      commented-out image classification stub
├── retrieval/
│   ├── assembler.py           EnsembleRetriever (BM25 + vector) hybrids
│   ├── bm_search.py           BM25 indexes built from data/raw
│   └── retriever.py           Pinecone vector retrievers + tools
├── schemas/
│   └── outputs.py             shared output schemas
└── vectorstore/
    └── vector.py              Pinecone client, embeddings (cached), namespaces
```

Top-level:

```text
run_api.py            uvicorn entrypoint (port 8000)
docker-compose.yml    Kafka broker + topic creation
requirements.txt      Python dependencies
evals/                LangSmith evaluation harness
tests/                pytest suite + k6 load test
client/               upload CLI client
data/raw/             source documents per topic
```

## Setup

### Requirements

- Python 3.13
- Postgres running locally (for the checkpointer); the connection string is `DB_URI`
- Kafka via Docker (see below)
- A Pinecone account and index
- A DeepSeek API key and a LangSmith API key

### Environment variables

Create `.env` from the names below (placeholders only; never commit real keys):

```text
DEEPSEEK_API_KEY=your-key
DB_URI=postgresql://user:pass@localhost:5432/myagri
MODEL_NAME=deepseek-flash
LANGSMITH_API_KEY=your-key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=agri-rag-api
PINECONE_API_KEY=your-key
PINECONE_INDEX=agri-rag-e5
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
RETRIEVAL_K=4
```

Optional settings: `LOG_LEVEL`, `CORS_ORIGINS`, `KAFKA_ENABLED`, `MAX_UPLOAD_MB`, `UPLOAD_DIR`, and the Kafka topic/broker settings (`KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC_RAW`, `KAFKA_TOPIC_CHUNKED`, `KAFKA_TOPIC_DLQ`). See `src/config/settings.py` for defaults.

### Start Kafka

```bash
docker compose up -d
```

This starts a single-node KRaft Kafka broker on `localhost:9092` and creates the `agri.docs.raw`, `agri.docs.chunked`, and `agri.docs.dlq` topics.

### Install and run

```bash
pip install -r requirements.txt
python run_api.py
```

The API serves on `http://localhost:8000` (docs at `/docs`).

## API reference

| Method | Path | Purpose |
| :--- | :--- | :--- |
| GET | `/` | Liveness + service name/version |
| GET | `/health` | Status, agent ready, Kafka connected |
| POST | `/chat` | Complete JSON answer |
| POST | `/chat/stream` | SSE token stream |
| POST | `/ingest` | Upload a document for ingestion |
| GET | `/ingest/{doc_id}` | Document status by id |

`/chat` and `/chat/stream` request body:

```json
{
  "question": "How much water does tomato need per season?",
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

- `question` (string, required)
- `thread_id` (UUID, required) — generated by the client; identifies the conversation thread.

`/ingest` multipart form fields:

| Field | Type | Required | Notes |
| :--- | :--- | :--- | :--- |
| `file` | file | yes | `.txt`, `.md`, `.pdf`, `.docx`, `.html`, `.htm`; max 20 MB |
| `topic` | string | yes | one of `soil`, `disease`, `water`, `crop_health`, `yield` |

Ingestion status lifecycle:

```text
received -> queued -> chunking -> chunked -> embedding -> indexed | failed
```

## Retrieval design

- **Per-topic namespaces.** Pinecone holds four namespaces: `soil`, `disease`, `water`, `yield`. `crop_health` has no namespace of its own and reuses `disease`.
- **Hybrid search.** Each topic is an `EnsembleRetriever` combining the BM25 keyword retriever with the Pinecone vector retriever (weights `[0.5, 0.55]`).
- **Keyword intent classifier.** `classify_intent` matches the question against word-boundary regex patterns per topic and fans out to the matching nodes in parallel (all four on no match).
- **Entry-aware chunking.** `split_documents` keeps a heading-delimited entry up to 1500 characters as one chunk and falls back to `RecursiveCharacterTextSplitter` otherwise.
- **`RETRIEVAL_K` (default 4).** Controls how many chunks each retriever returns, shared by the vector and BM25 sides.
- **Query embedding cache.** `_embed_query` is `@lru_cache`d (maxsize 512), so repeated queries reuse the cached vector instead of re-embedding.

## Evaluation and testing

Run the LangSmith evaluation harness:

```bash
python -m evals.run_eval
```

It evaluates the agent against the `agri-rag-eval-2` dataset using four LLM judges: helpfulness, groundedness, retrieval relevance, and correctness.

Run the test suite:

```bash
python -m pytest
```

## Observability

LangSmith tracing is enabled in `src/monitoring/tracing.py` (called before the LangChain/LangGraph imports). Chat runs use `run_name="agri-chat"` and `tags=["agri-api"]`. The API traces to the `agri-rag-api` project; the evaluation harness uses `agri-rag-eval`. Ingestion stages (`chunk_document`, `index_document`) are decorated with `@traceable`.

## Performance

Measured on a local dev machine with the reasoning mode disabled:

| Metric | Value |
| :--- | :--- |
| Median latency | ~3.0s |
| P95 latency | 5.87s |
| Input tokens per request | ~1,600 - 2,200 |
| Cost per request | ~$0.0001 - $0.0004 |
| Pinecone query/embed latency | ~2s network round-trip |

## Known limitations

- No authentication or rate limiting on the API.
- BM25 is in-memory only; it is rebuilt from indexed metadata on startup and lost on restart.
- No OCR for scanned PDFs (text extraction only; image-only PDFs yield no text).
- Embeddings require network access to the Pinecone Inference API (no local embedding).

## Roadmap

- Authentication and rate limiting.
- Postgres-backed metadata store instead of file-based JSON.
- Retry endpoint for failed/dead-lettered documents.
- Metrics dashboard.
- Local embedding option to remove the Pinecone network round-trip.
