import os
from dataclasses import dataclass
from typing import Any, List
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.usage import UsageLimits
from supabase import create_client

# Load environment variables
load_dotenv()

# Define the LLM model
llm = "llama-3.3-70b-versatile"

# Initialize Groq model
model = GroqModel(
    model_name=llm,
    api_key=os.getenv("GROQ_API_KEY"),
)

# Define dependencies
@dataclass
class Deps:
    supabase_url: str = os.getenv("SUPABASE_URL")
    supabase_key: str = os.getenv("SUPABASE_KEY")
    supabase_client: Any = create_client(supabase_url, supabase_key)

# Load the system prompt
with open("prompt.txt", "r") as file:
    prompt = file.read()

# Define usage limits
usage_limits = UsageLimits(response_tokens_limit=1500)

# Initialize the Pixy agent
VISU = Agent(
    model=model,
    system_prompt=prompt,
    deps_type=Deps,
    retries=3
)
