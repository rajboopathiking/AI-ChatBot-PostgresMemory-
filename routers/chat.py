
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from langchain_core.messages import HumanMessage
from ai_utils.agent.agent import Context
from ai_utils.memory import Store
from ai_utils.extract import extractor_llm

import inspect


router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


class ChatState(BaseModel):
    id: str
    message: str


@router.post("/invoke")
async def chat_(state: ChatState, request: Request):

    try:
        agent = request.app.state.agent
        store = request.app.state.store

        # Stable conversation ID
        session_id = state.id

        store_ = Store(
            store=store,
            id=session_id
        )

        # Retrieve existing long-term memory
        info = await store_.get()

        config = {
            "configurable": {
                "thread_id": session_id
            }
        }

        # Invoke LangGraph agent
        response = await agent.ainvoke(
            {
                "messages": [
                    HumanMessage(content=state.message)
                ]
            },
            config=config,
            context=Context(
                id=session_id,
                info=info
            )
        )

        messages = response["messages"]

        # Count human messages in the checkpointed conversation
        user_messages = [
            msg for msg in messages
            if msg.type == "human"
        ]

        message_count = len(user_messages)

        # Extract memory every 10 user messages
        if message_count > 0 and message_count % 10 == 0:

            # Construct conversation transcript
            conversation = "\n".join(
                f"{msg.type}: {msg.content}"
                for msg in messages
                if msg.type in ("human", "ai")
                and isinstance(msg.content, str)
            )

            # Extract updated long-term memory
            new_info = await extractor_llm.ainvoke(
    [
        (
            "system",
            """Extract useful long-term user memories from the conversation.

            Only extract information explicitly supported by the conversation.
            Avoid temporary questions and transient information.
            Do not invent facts.
            Return updated memory information."""
        ),
        (
            "human",
            conversation
        )
    ]
)

            # Convert Pydantic object to dictionary
            new_info = new_info.model_dump()

            if inspect.isawaitable(new_info):
                new_info = await new_info

            # Update persistent memory
            await store_.put(
                value=new_info
            )

            info = new_info

        # Get latest AI response
        ai_message = next(
            (
                msg for msg in reversed(messages)
                if msg.type == "ai" and msg.content
                and not msg.tool_calls
            ),
            None
        )

        if ai_message is None:
            raise HTTPException(
                status_code=500,
                detail="Agent did not produce an AI response"
            )

        return {
            "session_id": session_id,
            "response": ai_message.content,
            "message_count": message_count
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )