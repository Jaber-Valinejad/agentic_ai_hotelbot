<p align="center">
  <img src="https://github.com/Jaber-Valinejad/agentic_ai_hotelbot/blob/master/img/z13b.png" width="600"/>
</p>

---

# Agentic AI HotelBot

A multi-agent virtual concierge application powered by LangGraph, OpenAI, Redis, PostgreSQL, and FastAPI — designed for hotel information retrieval, reservation assistance, and intelligent query handling.

---

## 🧠 Project Overview

This system features:
- A **Supervisor Agent** with reasoning and memory
- A **RAG Agent** to retrieve FAQ-based information
- A **SQL Agent** to check room availability from the hotel database
- A **Redis vector store** for storing conversation memory
- A **FastAPI** backend serving outputs to an optional Streamlit UI

---

## 🧩 Repository Structure

```
agentic_ai_hotelbot/
├── src/                  <- Core agents and logic
│   ├── SupervisorAgent.py
│   ├── RagAgent.py
│   └── SqlAgent.py
├── api/                  <- FastAPI app setup
│   └── main.py
├── assets/               <- Diagrams or images
├── tests/                <- Unit and integration tests
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧪 Local Setup Instructions

### Python Virtual Environment

```bash
py -3.11 -m venv venv-py311
.
env-py311\Scripts ctivate
pip install -r requirements.txt
```

---

## 🛠 Poetry-based Environment

### Initial Setup

```bash
poetry init
poetry env use "path/to/python311"
poetry add torch transformers
poetry install
```

Check if llama-index is installed:
```bash
poetry show llama-index
```

To lock updated packages:

```bash
poetry lock --no-update
poetry install --no-root
```

Activate environment:

```bash
poetry shell
# Or run directly:
poetry run python my_script.py
```

---

## 💾 PostgreSQL & Redis Setup

### PostgreSQL (CLI)

```bash
psql -h <your-db-host> -U <your-username> -d <your-dbname>
\dt
```

### Redis (via Poetry)

```bash
poetry add redis
```

### Redis (Manual Installation)

1. [Download Redis](https://github.com/tporadowski/redis/releases)
2. Start Redis Server:
```bash
cd "path/to/Redis-x64"
redis-server.exe
```
3. Test Redis connection:
```bash
cd "path/to/Redis-x64"
.
edis-cli.exe ping
# Output: PONG
```

---

## ☁️ Neon PostgreSQL

1. Visit [https://neon.tech](https://neon.tech)
2. Sign up with GitHub or email
3. Create a new Postgres instance and connect using the credentials

---

## 🧪 Testing

Run tests:

```bash
pytest
pytest test_sql_agent.py -v
```

---

## 🚀 Running the Application

### FastAPI Backend

```bash
uvicorn week6_main:app --reload --port 8000
```

Access docs:
```
http://localhost:8000/docs
```

---

### Streamlit UI

```bash
streamlit run week6_main_Streamlit.py
```

Open:
```
http://localhost:8501
```

To stop Streamlit:
```bash
taskkill /f /im streamlit.exe
```

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
poetry self add poetry-plugin-export
poetry export -f requirements.txt --output requirements.txt --without-hashes
docker build -t bluehorizon-api .
```

---

### Run with Docker Compose

```bash
docker-compose up --build
```

If rebuild is needed:

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

Then visit: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📤 Docker Hub Deployment

1. Log in:
```bash
docker login
```

2. Tag & Push:

```bash
docker tag bluehorizon-api yourusername/bluehorizon-api:latest
docker push yourusername/bluehorizon-api:latest
```

View: [https://hub.docker.com/repositories/yourusername](https://hub.docker.com/repositories/yourusername)

---

## 🤗 Hugging Face Spaces Deployment

Create a new space → choose Docker → add this to `Dockerfile`:

```Dockerfile
FROM yourusername/bluehorizon-api:latest
EXPOSE 7860
```

After deployment, access:
```
https://yourusername--appname.hf.space/docs
```

---

## ☁️ AWS ECR Deployment

### Install AWS CLI

- [AWS CLI Download](https://aws.amazon.com/cli/)

### Authenticate Docker to ECR

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
```

### Tag & Push Docker Image

```bash
docker tag bluehorizon-api:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/bluehorizon-api:latest
docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/bluehorizon-api:latest
```

---

## 📦 Saving & Sharing Docker Image

Save image:

```bash
docker save myapp > myapp.tar
```

To share and run:

```bash
docker load < myapp.tar
docker run -p 8000:80 myapp
```

---

## 🧠 System Design Overview

- **Supervisor Agent**: Controls flow and memory, interprets intent.
- **RAG Agent**: Retrieves information from stored hotel FAQs.
- **SQL Agent**: Queries structured room and booking data.
- **Redis**: Stores embeddings and dialogue context.
- **FastAPI**: Hosts the backend inference and API.
- **Streamlit** *(optional)*: Lightweight frontend UI.

---

## 📬 Getting Help

- Open [GitHub Issues](https://github.com/Jaber-Valinejad/agentic_ai_hotelbot/issues)
- Use the GitHub **Discussions** tab for collaborative ideas and support.

---
