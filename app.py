from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from pydataui import mount

from ai_utils.memory import PostgresResource
from ai_utils.agent import build_agent
from routers import chat
from frontend import ui

load_dotenv()

resource = PostgresResource(
    db_uri=os.getenv("DB_URL")
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    await resource.start()

    checkpointer = resource.checkpointer
    store = resource.store

    agent = build_agent(
        checkpointer=checkpointer,
        store=store
    )

    app.state.checkpointer = checkpointer
    app.state.store = store
    app.state.agent = agent

    yield

    await resource.close()


app = FastAPI(
    title="ChatBot (PostgreSQL Memory)",
    lifespan=lifespan
)

# Register API routes first
app.include_router(chat.router)

# Mount PyDataUI
mount(app, ui, path="/")