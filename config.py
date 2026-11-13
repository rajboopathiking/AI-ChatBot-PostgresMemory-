import os
from dotenv import load_dotenv

load_dotenv()

from dataclasses import dataclass


@dataclass
class Config:
  model_name : str = "gemini-2.5-flash"
  gemini_api_key : str = os.getenv("GOOGLE_API_KEY")
  database_url : str = os.getenv("DB_URL")
  
