# Desafio MBA Engenharia de Software com IA - Full Cycle

## Descrição do Projeto

Este projeto implementa um sistema RAG (Retrieval-Augmented Generation) para ingestão de documentos e busca inteligente. O sistema processa documentos PDF, cria embeddings vetoriais e fornece capacidades de perguntas e respostas contextuais com aderência estrita ao material fonte.

### Arquitetura

O sistema segue um pipeline modular ETL + RAG:

- **Ingestão** (`src/ingest.py`): Pipeline de ingestão de documentos (PDF → chunks de texto → embeddings → armazenamento vetorial)
- **Busca** (`src/search.py`): Funcionalidade RAG central (busca vetorial + integração LLM)
- **Chat** (`src/chat.py`): Interface de chat interativa que utiliza search.py

**Fluxo de Dados**: PDF → Chunks de Texto → Embeddings → PostgreSQL/pgvector → Busca Vetorial → LLM → Resposta

## Ferramentas Necessárias

- **Python 3.11+**
- **Docker** e **Docker Compose**
- **Git** (para clonar o repositório)
- Conta **OpenAI** com API key (ou Google AI como alternativa)

## Como Executar a Solução

### 1. Configuração do Ambiente Python

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Linux/Mac:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configuração de Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar o arquivo .env com suas configurações:
# - OPENAI_API_KEY: Sua chave da API OpenAI
# - PGVECTOR_URL: postgresql://postgres:postgres@localhost:5432/rag
# - PG_VECTOR_COLLECTION_NAME: meu_documento
# - PDF_PATH: ./document.pdf
```

### 3. Inicializar Banco de Dados

```bash
# Iniciar PostgreSQL com extensão pgvector
docker-compose up -d

# Verificar se os serviços estão rodando
docker-compose ps
```

### 4. Executar Ingestão de Documentos

```bash
# Processar e armazenar o documento PDF
python src/ingest.py
```

Este comando irá:
- Carregar o documento PDF especificado em PDF_PATH
- Dividir o texto em chunks
- Gerar embeddings usando OpenAI
- Armazenar os vetores no PostgreSQL

### 5. Iniciar Chat Interativo

```bash
# Iniciar interface de chat
python src/chat.py
```

Agora você pode fazer perguntas sobre o conteúdo do documento ingerido. O sistema responderá apenas com base no contexto do documento fornecido.

## Exemplos de Uso

### Perguntas que serão respondidas:
- "Qual é o assunto principal do documento?"
- "Quais são os pontos importantes mencionados?"
- "O que o documento diz sobre [tópico específico]?"

### Perguntas que retornarão "Não tenho informações necessárias":
- "Qual é a capital da França?" (conhecimento externo)
- "O que você acha sobre isso?" (opinião)
- "Quantos clientes temos?" (informação não presente no documento)

## Comandos Úteis

### Gerenciamento do Banco de Dados
```bash
# Parar serviços
docker-compose down

# Resetar banco (remove todos os dados)
docker-compose down -v
docker-compose up -d
```

### Reprocessar Documentos
```bash
# Para adicionar novos documentos, execute novamente:
python src/ingest.py
```

## Tecnologias Utilizadas

- **LangChain**: Framework para pipeline RAG
- **OpenAI**: Embeddings e modelo de linguagem
- **PostgreSQL + pgvector**: Banco de dados vetorial
- **Docker**: Containerização do banco de dados
- **Python**: Linguagem de desenvolvimento

## Estrutura do Projeto

```
├── README.md                 # Este arquivo
├── CLAUDE.md                 # Documentação para Claude Code
├── requirements.txt          # Dependências Python
├── docker-compose.yml        # Configuração PostgreSQL + pgvector
├── document.pdf             # Documento de exemplo
├── .env.example             # Template de configuração
└── src/                     # Código fonte
    ├── ingest.py            # Pipeline de ingestão
    ├── search.py            # Busca vetorial e LLM
    └── chat.py              # Interface de chat
```

## Resolução de Problemas

### Erro de conexão com banco de dados
- Verifique se o Docker está rodando: `docker ps`
- Reinicie os serviços: `docker-compose restart`

### Erro de API Key
- Verifique se OPENAI_API_KEY está configurada no arquivo .env
- Confirme se a chave é válida e tem créditos disponíveis

### Documento não encontrado
- Verifique se o arquivo especificado em PDF_PATH existe
- Confirme se o caminho está correto no arquivo .env