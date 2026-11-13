from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt,ModelRequest
from langchain_google_genai import ChatGoogleGenerativeAI
from dataclasses import dataclass
from typing import Optional,Any
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Context:
  id : str
  info : dict

@dynamic_prompt
async def dynamic_system_prompt(request:ModelRequest):
  context = request.runtime.context.info
  system_prompt = f"""You are AI Assistant, 
  Handle user in perferable calm way
  context : {context}

"""
  return system_prompt

llm = ChatGoogleGenerativeAI(
  model="gemini-2.5-flash",
  temperature = 0.5
)

def build_agent(checkpointer,store):
  agent = create_agent(
    model=llm,
    tools = [],
    context_schema=Context,
    middleware=[dynamic_system_prompt],
    checkpointer = checkpointer,
    store = store
  )
  return agent

