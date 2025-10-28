# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) system for document ingestion and intelligent search. The system processes PDF documents, creates vector embeddings, and provides contextual Q&A capabilities with strict adherence to source material.

## Architecture

The system follows a modular ETL + RAG pipeline:

- **`src/ingest.py`**: Document ingestion pipeline (PDF → text chunks → embeddings → vector storage)
- **`src/search.py`**: Core RAG functionality (vector search + LLM integration)
- **`src/chat.py`**: Interactive chat interface that uses search.py

**Data Flow**: PDF → Text Chunks → Embeddings → PostgreSQL/pgvector → Vector Search → LLM → Response

## Common Development Commands

### Environment Setup
```bash
# Copy environment template and configure
cp .env.example .env
# Edit .env with your API keys and database settings

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL with pgvector extension
docker-compose up -d
```

### Running the Application
```bash
# Step 1: Ingest documents (run once or when adding new documents)
python src/ingest.py

# Step 2: Start interactive chat
python src/chat.py
```

### Database Management
```bash
# Start database services
docker-compose up -d

# Stop database services
docker-compose down

# Reset database (removes all data)
docker-compose down -v
docker-compose up -d
```

## Key Configuration

Environment variables in `.env`:
- **`OPENAI_API_KEY`**: Required for embeddings and LLM
- **`OPENAI_EMBEDDING_MODEL`**: Embedding model (default: text-embedding-3-small)
- **`PGVECTOR_URL`**: PostgreSQL connection string
- **`PG_VECTOR_COLLECTION_NAME`**: Collection name for vector storage
- **`PDF_PATH`**: Path to document for ingestion

## Architecture Details

### Vector Database Setup
- Uses PostgreSQL 17 with pgvector extension
- Automatic extension initialization via bootstrap service
- Default database: `rag` (user: postgres, password: postgres)
- Port: 5432

### RAG Implementation
- **Chunking**: Text split into manageable pieces during ingestion
- **Embeddings**: OpenAI text-embedding-3-small (configurable)
- **Vector Search**: Top-k similarity search (k=10)
- **LLM**: ChatOpenAI with gpt-5-nano, temperature=0
- **Prompt Engineering**: Strict rules to prevent hallucination

### Critical Implementation Details

**Defensive Prompting** (src/search.py:13-38):
The system uses strict prompt templates that:
- Only respond based on provided context
- Return "Não tenho informações necessárias para responder sua pergunta." for out-of-scope queries
- Prevent hallucination and external knowledge usage
- Maintain factual accuracy to source documents

**Vector Search Configuration**:
- Uses `similarity_search_with_score()` with k=10
- Falls back to "no information" response if no relevant context found
- Concatenates multiple document chunks with separator (`---`)

## Dependencies

**Core Framework**: LangChain ecosystem for RAG pipeline
**Database**: PostgreSQL with pgvector for vector storage
**AI Services**: OpenAI for embeddings and LLM (alternative: Google AI)
**Document Processing**: PyPDF for PDF parsing
**Environment**: python-dotenv for configuration

## Development Notes

- No testing framework currently implemented
- Database connection string uses PGVECTOR_URL environment variable
- Vector collection names are configurable via PG_VECTOR_COLLECTION_NAME
- The system is designed for single-document processing (document.pdf)
- LLM responses are strictly bounded by retrieved context to prevent hallucination

## Workflow Dependencies

1. **Database must be running** before ingestion or chat
2. **Ingestion must complete** before meaningful chat interactions
3. **Environment variables must be configured** for all operations
4. **API keys required** for OpenAI services (or Google AI alternative)

## Error Handling Patterns

The codebase implements defensive patterns:
- Graceful fallbacks when no context is found
- Environment variable validation through getenv() with defaults
- Database connection health checks in docker-compose
- Strict prompt adherence to prevent AI hallucination