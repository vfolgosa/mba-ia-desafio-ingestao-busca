from ast import List
import os
from langchain_core.documents import Document
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_core.messages import HumanMessage
from typing import List, Tuple

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
""".strip()

PGVECTOR_COLLECTION = os.getenv("PG_VECTOR_COLLECTION_NAME") or "default_collection"
PGVECTOR_URL = os.getenv("PGVECTOR_URL") or None

def _get_vector_store():
    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL","text-embedding-3-small"))
    store = PGVector(
        embeddings=embeddings,
        collection_name=PGVECTOR_COLLECTION,
        connection=PGVECTOR_URL,
        use_jsonb=True,
    )
    return store

def _concat_context(results: List[Tuple[Document, float]]) -> str:
    parts = []
    for doc, _score in results:
        parts.append(doc.page_content.strip())
    return "\n\n---\n\n".join(parts) if parts else ""

def _call_llm(prompt: str) -> str:
    llm = ChatOpenAI(model="gpt-5-nano", temperature=0)
    resp = llm.invoke([HumanMessage(content=prompt)])
    return resp.content.strip()
      
def _build_prompt(pergunta: str, contexto: str) -> str:
    return PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta)
        
def search_prompt():
  
  store = _get_vector_store()
  
  def run(question: str) -> str:
        # 1) Recuperar top-k
        results = store.similarity_search_with_score(question, k=10)

        # 2) Se não houver contexto, responde diretamente conforme a regra
        if not results:
            return 'Não tenho informações necessárias para responder sua pergunta.'

        # 3) Montar contexto + prompt
        contexto = _concat_context(results)
        if not contexto.strip():
            return 'Não tenho informações necessárias para responder sua pergunta.'

        prompt = _build_prompt(question, contexto)

        # 4) Chamar LLM
        answer = _call_llm(prompt)
        return answer
  return run