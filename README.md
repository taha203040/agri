# 🌱 Agriculture RAG

An MVP **Retrieval-Augmented Generation (RAG)** application designed to answer agriculture-related questions using a knowledge base of agricultural documents.

The system combines **semantic search**, **vector storage**, and an **AI language model** to retrieve relevant agricultural knowledge before generating an answer.

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
Backend API
 │
 ├──────────────► Embedding Model
 │                    │
 │                    ▼
 │              Query Embedding
 │                    │
 │                    ▼
 │              Vector Database
 │                    │
 │                    ▼
 │              Relevant Documents
 │                    │
 │                    ▼
 └──────────────► AI / LLM
                       │
                       ▼
                  Generated Answer
                       │
                       ▼
                    User
```

The main idea is to **retrieve relevant agricultural information first**, then provide that context to the LLM so that the generated answer is grounded in the application's knowledge base.

---

## 🎯 Objectives

* Provide agriculture-specific answers.
* Reduce hallucinations by grounding responses in retrieved documents.
* Search agricultural knowledge using semantic similarity.
* Support an extensible knowledge base.
* Keep the architecture simple enough for an MVP.
* Allow the system to evolve toward a production architecture.

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
                    │    Backend      │
                    │     API         │
                    └───────┬─────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
        ┌─────────────────┐    ┌─────────────────┐
        │ Embedding Model │    │       LLM       │
        └────────┬────────┘    └────────┬────────┘
                 │                      │
                 ▼                      │
        ┌─────────────────┐             │
        │  Vector Store   │◄────────────┘
        └─────────────────┘
```

---

## 🔄 RAG Request Flow

When a user asks a question:

### 1. User sends a question

```text
"What causes yellow leaves in tomato plants?"
```

The frontend sends the question to the backend.

### 2. Query embedding

The backend sends the question to an embedding model.

```text
Question
   │
   ▼
Embedding Model
   │
   ▼
Vector
```

The text is converted into a numerical vector representing its semantic meaning.

### 3. Vector search

The generated vector is compared with vectors stored in the vector database.

```text
Query Vector
     │
     ▼
Vector Database
     │
     ├── Document A
     ├── Document B
     ├── Document C
     └── Document D
```

The most semantically relevant documents are retrieved.

### 4. Context construction

The retrieved documents are combined with the original question.

```text
Question
   +
Retrieved Context
   ↓
Prompt
```

### 5. LLM generation

The prompt is sent to the language model.

```text
Prompt
  │
  ▼
LLM
  │
  ▼
Agricultural Answer
```

### 6. Response

The generated answer is returned to the frontend.

---

## ⚡ Sync and Async Processing

The application separates operations that are required for the user's immediate request from background processing.

### Synchronous request

The user-facing RAG query is synchronous:

```text
User
 │
 ▼
API
 │
 ▼
Embedding
 │
 ▼
Vector Search
 │
 ▼
LLM
 │
 ▼
Response
 │
 ▼
User
```

The user waits for the final answer.

### Asynchronous processing

Knowledge ingestion can be performed asynchronously.

```text
Agricultural Document
        │
        ▼
   Background Job
        │
        ▼
     Chunking
        │
        ▼
    Embedding
        │
        ▼
   Vector Store
```

This prevents expensive document-processing operations from blocking the main API.

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
Embedding Model
   │
   ▼
Vector Database
```

Each document is divided into smaller chunks.

Each chunk contains:

* Text
* Embedding
* Metadata
* Document identifier
* Optional source information

Example:

```json
{
  "text": "Tomato plants require...",
  "metadata": {
    "source": "agriculture-guide.pdf",
    "topic": "tomato",
    "category": "plant-disease"
  }
}
```

---

## 🔎 Retrieval

The retrieval stage performs semantic similarity search.

For example:

```text
User Query:
"Why are my tomato leaves turning yellow?"

             ↓

        Query Embedding

             ↓

      Vector Similarity Search

             ↓

┌──────────────────────────────┐
│ Relevant agricultural chunks │
├──────────────────────────────┤
│ Tomato nutrient deficiency   │
│ Tomato plant diseases        │
│ Irrigation problems          │
└──────────────────────────────┘
```

The top relevant chunks are then provided to the LLM as context.

---

## 🧠 Generation

The LLM receives a prompt containing:

```text
System Instructions
        +
User Question
        +
Retrieved Agricultural Context
```

Conceptually:

```text
You are an agriculture assistant.

Use the following agricultural knowledge:

[Retrieved Document 1]

[Retrieved Document 2]

[Retrieved Document 3]

Question:

Why are my tomato leaves turning yellow?
```

The model generates the final response using the retrieved information.

---

## 🗂️ Project Structure

A possible project structure:

```text
agriculture-rag/
│
├── frontend/
│   ├── src/
│   └── ...
│
├── backend/
│   ├── src/
│   │   ├── api/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   └── ...
│   │
│   └── ...
│
├── ingestion/
│   ├── loaders/
│   ├── chunking/
│   ├── embeddings/
│   └── ...
│
├── documents/
│   └── ...
│
├── docker/
│   └── ...
│
└── README.md
```

---

## 🧱 Main Components

| Component          | Responsibility                   |
| ------------------ | -------------------------------- |
| Frontend           | User interface                   |
| Backend API        | Handles application requests     |
| Embedding Model    | Converts text into vectors       |
| Vector Store       | Stores and searches embeddings   |
| Retriever          | Finds relevant documents         |
| LLM                | Generates the final response     |
| Ingestion Pipeline | Processes agricultural documents |

---

## 🛠️ Technology Stack

The exact implementation can evolve, but the architecture is designed around:

* **Frontend:** React / Next.js
* **Backend:** Python or Node.js
* **RAG:** LangChain / LangGraph
* **Embeddings:** Hugging Face or another embedding provider
* **Vector Store:** PostgreSQL with `pgvector` or another vector database
* **LLM:** OpenAI / compatible LLM provider
* **Containerization:** Docker
* **Cloud:** AWS

---

## ☁️ AWS Deployment

For production, the architecture can be deployed using AWS services.

```text
                    ┌──────────────┐
                    │    Client    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ API Gateway  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ ECS / App    │
                    │   Backend    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
         Embeddings    Vector DB       LLM
              │
              ▼
       Retrieved Context
```

Background ingestion can be separated from the API:

```text
S3
 │
 ▼
Background Worker
 │
 ▼
Document Processing
 │
 ▼
Embeddings
 │
 ▼
Vector Database
```

This allows ingestion to scale independently from user requests.

---

## 🚀 MVP Scope

The initial version focuses on the core RAG pipeline:

* [x] Agricultural document ingestion
* [x] Document chunking
* [x] Embedding generation
* [x] Vector storage
* [x] Semantic retrieval
* [x] LLM generation
* [x] REST API
* [x] Frontend integration
* [ ] Authentication
* [ ] Advanced observability
* [ ] Production autoscaling
* [ ] Advanced evaluation

---

## 🧪 Example

### User

```text
What causes brown spots on tomato leaves?
```

### Retrieval

The system searches the agricultural vector database and retrieves relevant information about:

```text
Tomato diseases
Fungal infections
Leaf spot diseases
Environmental stress
```

### Generation

The LLM uses the retrieved information to generate an answer explaining possible causes and recommended actions.

---

## ⚠️ Important Limitation

The system should not treat generated answers as a replacement for professional agricultural diagnosis.

RAG improves grounding by providing relevant knowledge to the model, but the final answer can still be incorrect if:

* The knowledge base is incomplete.
* Retrieved documents are irrelevant.
* The embedding model performs poorly.
* The LLM misinterprets the retrieved context.

For this reason, source attribution and RAG evaluation should be added as the project matures.

---

## 📈 Future Improvements

Potential improvements include:

1. **Hybrid Search**

   * Combine vector similarity with keyword search.

2. **Reranking**

   * Rerank retrieved documents using a dedicated reranker.

3. **Source Citations**

   * Show the agricultural document used for each answer.

4. **RAG Evaluation**

   * Measure retrieval relevance and answer faithfulness.

5. **Image-Based Diagnosis**

   * Integrate plant-disease image classification.

6. **Conversation Memory**

   * Maintain context across multiple questions.

7. **Streaming**

   * Stream generated responses to the frontend.

8. **Production Infrastructure**

   * ECS, S3, managed databases, monitoring, logging, and autoscaling.

---

## 📊 High-Level Architecture

```text
                         AGRICULTURE RAG
                              │
              ┌───────────────┴───────────────┐
              │                               │
        USER QUERY                      KNOWLEDGE INGESTION
              │                               │
              ▼                               ▼
        Backend API                       Documents
              │                               │
              ▼                               ▼
        Query Embedding                  Text Extraction
              │                               │
              ▼                               ▼
        Vector Search                     Chunking
              │                               │
              ▼                               ▼
      Relevant Documents                 Embeddings
              │                               │
              └──────────────┬────────────────┘
                             ▼
                            LLM
                             │
                             ▼
                    Grounded Answer
                             │
                             ▼
                           User
```

---

## 📄 License

This project is intended for educational, experimental, and MVP development purposes.
