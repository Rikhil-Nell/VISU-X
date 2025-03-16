from dataclasses import dataclass
from typing import Any
from settings import Settings
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel, GroqModelSettings
from supabase import create_client

settings = Settings()

llm = "llama-3.3-70b-versatile"

# Define Groq model settings
groq_settings = GroqModelSettings(
    temperature=0.7,
    max_tokens=500,
    top_p=0.95,
    frequency_penalty=0,
)

# Initialize Groq model
model = GroqModel(
    model_name=llm,
    api_key=settings.groq_key,
)

emotion_model = GroqModel(
    model_name=llm,
    api_key=settings.groq_key,
)

# Define dependencies
@dataclass
class Deps:
    supabase_url: str = settings.supabase_url
    supabase_key: str = settings.supabase_key
    supabase_client: Any = create_client(supabase_url, supabase_key)


# Load the system prompt
with open("prompt.txt", "r") as file:
    prompt = file.read()

# Initialize the Pixy agent
VISU = Agent(
    model=model,
    model_settings=groq_settings,
    system_prompt=prompt,
    deps_type=Deps,
    retries=3,
)

# Initialize the emotion agent
emotion_agent = Agent(
    model=emotion_model,
    model_settings=groq_settings,
    deps_type=Deps,
    retries=3,
)

@VISU.tool_plain()
async def wave_hand() -> None:
    """Wave your robotic arm to the user when you detect a greeting or goodbye."""
    print("Waving hand...")
    # Code to wave the robotic arm
    