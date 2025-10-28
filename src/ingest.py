import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH") or None
PGVECTOR_COLLECTION = os.getenv("PG_VECTOR_COLLECTION_NAME") or "default_collection"
PGVECTOR_URL = os.getenv("PGVECTOR_URL") or None
def ingest_pdf():
    if PDF_PATH is None:
        raise ValueError("PDF_PATH environment variable is not set.")

    loader = PyPDFLoader(PDF_PATH)
    data = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150, add_start_index=False)
    data = splitter.split_documents(data)

    if not data:
        raise ValueError("No data was loaded from the PDF.")
    
    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in data
    ]
    
    ids = [f"doc-{i}" for i in range(len(enriched))]
    
    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL","text-embedding-3-small"))
    
    store = PGVector(
        embeddings=embeddings,
        collection_name=PGVECTOR_COLLECTION,
        connection=PGVECTOR_URL,
        use_jsonb=True,
    )
    
    store.add_documents(documents=enriched, ids=ids)



if __name__ == "__main__":
    ingest_pdf()