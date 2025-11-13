# RAG Chat Module — Requirements (Gemini)

## 1. Goal
Provide a single QA endpoint that answers student questions about NCERT content (classes 8–12) using a Retrieval-Augmented Generation (RAG) approach.  
Answers must be grounded in stored textbook chunks (pgvector) and cite sources.

---

## 2. Actors
- **Student / Client** — submits a question and optional filters.  
- **API** — returns an answer, sources, and metadata.  
- **Admin / Operator** — monitors logs and performance.

---

## 3. High-level functional requirements
1. **Single endpoint**: `POST /chat/ask` — accepts a question and optional filters (class, subject, chapter, top_k).  
2. **Filtering**: When provided, `class`, `subject`, and `chapter` restrict retrieval to matching chunks.  
3. **Retrieval**: Query pgvector-backed `content_chunk` table to find relevant chunks using vector similarity.  
4. **Reranking (optional)**: Support optional reranking of initial candidates (flag `re_rank`).  
5. **Prompt assembly**: Build a prompt consisting of retrieved snippets + user question + instructions to the LLM to cite sources and avoid hallucination.  
6. **LLM**: Use Gemini model (cloud) to generate final answer with low temperature (deterministic).  
7. **Citations**: Each fact in the answer must include `[source_index]` mapped to chunk metadata.  
8. **Fallback**: If retrieval finds no useful chunks, return `"I don't know based on provided texts."`  
9. **Response metadata**: Include `retrieved_count`, `top_k`, `llm_latency_ms`, etc.  

---

## 4. API contract

### Request
`POST /chat/ask`  
Content-Type: `application/json`

```json
{
  "question": "Why do tides happen?",
  "class": 10,
  "subject": "Science",
  "chapter": "Tides",
  "top_k": 8,
  "re_rank": true
}
```

### Response (200)
```json
{
  "answer": "Tides occur due to the gravitational pull of the moon and sun on Earth’s oceans. [1]",
  "sources": [
    {
      "chunk_id": 123,
      "source_file": "10th-science.pdf",
      "page": 12,
      "snippet": "Tides are caused by the gravitational attraction..."
    }
  ],
  "metadata": {
    "retrieved": 50,
    "used_top_k": 8,
    "re_ranked": true
  },
  "llm_usage": {
    "latency_ms": 1200,
    "tokens": 512
  }
}
```

### Errors
- `400`: Invalid input (missing `question`, bad params)
- `429`: Too many requests
- `503`: LLM unavailable or timeout
- `500`: Internal server error

---

## 5. Retrieval pipeline
1. **Validate** request and normalize filters.  
2. **Embed** the user question (using same model as used for document embeddings).  
3. **Search** similar vectors in `content_chunk` ordered by similarity (`embedding <-> query_vector`).  
4. **Filter** by class, subject, chapter if provided.  
5. **Select top-K** results for context.  
6. **Assemble prompt**: include snippets + question + instructions.  
7. **Send to Gemini** and parse the structured output with citations.  
8. **Return** answer, sources, and metadata.

---

## 6. Prompt structure

**System prompt:**
```
You are a helpful assistant answering questions based ONLY on the provided textbook excerpts.
Always cite source pages like [1]. If answer not found, say: "I don't know based on provided texts."
```

**Template:**
```
-- CONTEXT START --
[1] (file: {source_file} page: {page}) {snippet}
[2] ...
-- CONTEXT END --

Question: {question}
```

LLM params: `temperature=0.1`, `max_tokens` tuned to output size.

---

## 7. Response logic
- Answer should be concise and cite sources `[n]`.  
- If retrieval similarity < threshold or empty → fallback message.  
- Include metadata about retrieval and performance.

---

## 8. Performance and caching
- Cache embeddings for repeated questions (optional).  
- Limit context length to avoid token overflow.  
- Retrieve up to 50 chunks; select top 8.  
- LLM timeout: 30 seconds max.

---

## 9. Error handling
- Retry LLM calls 3 times with exponential backoff.  
- On timeout → return fallback message with top snippets.  
- Handle all DB/LLM exceptions gracefully.

---

## 10. Observability
- Log each request with latency and retrieval count.  
- Track metrics like `llm_latency_ms` and `retrieval_time_ms`.  

---

## 11. Data assumptions
- `content_chunk` table exists with:  
  `id, source_file, class_name, subject, chapter, page, text, embedding`.  
- Embeddings stored in pgvector (indexed).  

---

## 12. Example curl

```bash
curl -X POST "http://127.0.0.1:8000/chat/ask"   -H "Content-Type: application/json"   -d '{"question": "Why do tides happen?", "class": 10, "subject": "Science", "top_k": 6}'
```

---

✅ **Acceptance Criteria**
- Correct and grounded answer with citations  
- Fallback message when no data found  
- Response under 10s average latency  
- Logs and metrics captured for all calls  

---
