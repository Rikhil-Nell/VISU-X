from dataclasses import dataclass
from typing import Any
from settings import Settings
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel, GroqModelSettings, GroqModelName
from pydantic_ai.providers.groq import GroqProvider
from supabase import create_client
from pydantic import BaseModel, Field
settings = Settings()

model_name : GroqModelName = "llama-3.3-70b-versatile"

# Define Groq model settings
groq_settings = GroqModelSettings(
    temperature=0.7,
    max_tokens=500,
    top_p=0.95,
    frequency_penalty=0,
)

# Initialize Groq model
model = GroqModel(
#    provider="groq",
    model_name=model_name,
    provider=GroqProvider(api_key=settings.groq_key)
)

emotion_model = GroqModel(
#    provider="groq",
    model_name=model_name,
    provider=GroqProvider(api_key=settings.groq_key)
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

# Load the emotion analysis template
with open("face_emotion.txt", "r") as file:
    emotion_prompt = file.read()

# result type
emotions : str = "happy, sad, confused, neutral, angry, focused"

class emotion(BaseModel):
    emotionofuser: str = Field(description=f"The emotion of the user based on conversation history from the list: {emotions}")
    emotionofbot: str = Field(description=f"The emotion of the bot based on conversation history from the list: {emotions}")

# Initialize the Pixy agent
VISU = Agent(
    model=model,
    model_settings=groq_settings,
    system_prompt=prompt,
    deps_type=Deps,
)

# Initialize the emotion agent
emotion_agent = Agent(
    model=emotion_model,
    model_settings=groq_settings,
    deps_type=Deps,
    system_prompt=emotion_prompt,
    result_type=emotion,
)

async def wave_hand() -> None:
    """Wave your robotic arm to the user when you detect a greeting or goodbye."""

    print("Waving hand...")
    # Code to wave the robotic arm
    