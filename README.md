# AI Chatbot with PostgreSQL Long-Term Memory & Checkpointing

A production-ready conversational AI agent built with **FastAPI**, **LangGraph**, **Google Gemini**, and **PostgreSQL**. The system features hybrid memory architecture: short-term conversation thread checkpointing combined with structured long-term user memory extraction stored in PostgreSQL.

---

## 🚀 Key Features

- **Conversational AI with Gemini**: Powered by Google's `gemini-2.5-flash` model using LangChain / LangGraph.
- **Short-Term Memory (Thread Checkpointing)**: Built with `AsyncPostgresSaver` via `langgraph-checkpoint-postgres`, enabling stateful multi-turn dialogues across sessions.
- **Long-Term Memory (Store & Semantic Memory Extraction)**: Periodic automatic extraction (every 10 user turns) of user profiles, preferences, personal facts, ongoing projects, and persistent instructions using structured Pydantic schemas stored in `AsyncPostgresStore`.
- **Dynamic Context Injection**: Dynamic system prompts injected via LangChain agent middleware that adapt based on the user's persisted long-term profile.
- **FastAPI REST API**: High-performance asynchronous backend exposing conversational endpoints (`/chat/invoke`).
- **Interactive Web Interface**: Built-in reactive chat UI using `pydataui` mounted directly on the FastAPI server.
- **Connection Pooling**: Managed via `psycopg_pool.AsyncConnectionPool` for robust PostgreSQL connections.

---

## 🏗️ Architecture & Flow

```
                      +-----------------------------+
                      |   PyDataUI Web Frontend     |
                      |    (Mounted at '/')         |
                      +--------------+--------------+
                                     |
                             HTTP POST /chat/invoke
                                     v
                      +-----------------------------+
                      |       FastAPI Router        |
                      +--------------+--------------+
                                     |
          +--------------------------+--------------------------+
          |                                                     |
          v                                                     v
+--------------------+                               +--------------------+
| AsyncPostgresSaver |                               | AsyncPostgresStore |
| (Thread Memory)    |                               | (Long-Term Memory) |
+---------+----------+                               +----------+---------+
          |                                                     |
          +--------------------------+--------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |   LangGraph Agent Runner    |
                      | (Gemini 2.5 Flash + Context)|
                      +--------------+--------------+
                                     |
            Every 10 Turns: Structured Memory Extractor
                                     |
                                     v
                      +-----------------------------+
                      | Updates Long-Term Facts &   |
                      | Preferences in PostgresStore|
                      +-----------------------------+
```

---

## 📁 Project Structure

```text
chatbot-ai/
├── ai_utils/
│   ├── agent/
│   │   ├── __init__.py
│   │   └── agent.py              # Agent definition & dynamic prompt middleware
│   ├── extract/
│   │   ├── __init__.py
│   │   └── extractor.py          # Structured Pydantic extractor for memory
│   └── memory/
│       ├── __init__.py
│       └── memory.py             # PostgreSQL connection pool, checkpointer & store
├── dist/
│   └── index.html                # Static UI distribution assets
├── routers/
│   ├── __init__.py
│   └── chat.py                   # FastAPI /chat endpoints & memory update triggers
├── app.py                        # FastAPI application entrypoint & lifespan
├── config.py                     # Environment and configuration settings
├── frontend.py                   # PyDataUI reactive frontend interface
├── requirements.txt              # Project dependencies
├── LICENSE                       # License information
└── README.md                     # Documentation
```

---

## 🛠️ Prerequisites

- **Python**: Version `3.11` or `3.12` recommended.
- **PostgreSQL**: A running PostgreSQL database instance (local or hosted, e.g., Neon, Supabase, RDS).
- **Google Gemini API Key**: Obtainable from [Google AI Studio](https://aistudio.google.com/).

---

## ⚙️ Installation & Setup

### 1. Clone the Repository & Navigate to Directory
```bash
git clone <repository-url>
cd chatbot-ai
```

### 2. Set Up a Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root of `chatbot-ai`:

```env
# Google Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key_here

# PostgreSQL Connection String
DB_URL=postgresql://username:password@localhost:5432/your_database_name
```

> **Note**: Ensure your PostgreSQL user has permission to create tables. LangGraph will automatically execute table setup for checkpoints and store on startup.

---

## 🚦 Running the Application

### Development Server (Uvicorn)
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Production Server (Granian)
```bash
granian --interface asgi app:app --host 0.0.0.0 --port 8000
```

Once running:
- **Interactive Chat UI**: Open your browser at [http://localhost:8000/](http://localhost:8000/)
- **API Documentation (Swagger UI)**: Visit [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs (ReDoc)**: Visit [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔌 API Reference

### Invoke Chat

Sends a message into the conversation thread, retrieves context from long-term memory, and returns the assistant's reply.

- **Endpoint**: `POST /chat/invoke`
- **Headers**: `Content-Type: application/json`

#### Request Body
```json
{
  "id": "user_session_123",
  "message": "Hello, my name is Alex and I'm developing a React Native app."
}
```

#### Response (`200 OK`)
```json
{
  "session_id": "user_session_123",
  "response": "Hello Alex! Nice to meet you. How is your React Native project going?",
  "message_count": 1
}
```

---

## 🧠 Memory Architecture Details

1. **Short-Term Thread History (`AsyncPostgresSaver`)**:
   - Persists all message exchanges (`HumanMessage`, `AIMessage`, etc.) per `thread_id`.
   - Allows the conversation to resume seamlessly across server restarts and user reconnects.

2. **Long-Term Memory Extraction (`Extractor`)**:
   - Every **10 messages**, an extraction pipeline triggers using structured outputs.
   - Extracts four key dimensions:
     - `preferences`: User habits, tool choices, and style preferences.
     - `personal_facts`: Explicit user information (name, role, background).
     - `ongoing_projects`: Current tasks and development status.
     - `instructions`: Ongoing guidelines provided by the user.
   - Stored in `AsyncPostgresStore` under the `("user", session_id)` namespace and automatically injected into subsequent conversations via dynamic prompt middleware.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more details.
