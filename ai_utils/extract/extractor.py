
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict
from typing import List

load_dotenv()


class Extractor(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    preferences: List[str] = Field(
        default_factory=list,
        description="User preferences and interests"
    )

    personal_facts: List[str] = Field(
        default_factory=list,
        description="Useful facts explicitly shared by the user"
    )

    ongoing_projects: List[str] = Field(
        default_factory=list,
        description="Current projects and their progress"
    )

    instructions: List[str] = Field(
        default_factory=list,
        description="Persistent instructions from the user"
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

extractor_llm = llm.with_structured_output(Extractor)
