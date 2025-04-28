from dataclasses import dataclass
from typing import Any
from settings import Settings
from pi_serial import send_number_to_rpi
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel, GroqModelSettings, GroqModelName
from pydantic_ai.providers.groq import GroqProvider
from pydantic_ai.models.openai import OpenAIModel, OpenAIModelSettings, OpenAIModelName
from pydantic_ai.providers.openai import OpenAIProvider
from supabase import create_client
from pydantic import BaseModel, Field
settings = Settings()


visu_model_name : GroqModelName = "llama-3.3-70b-versatile"

# visu_model_name : OpenAIModelName = "chatgpt-4o-latest"

emotion_model_name : GroqModelName = "llama-3.3-70b-versatile"

# Define Groq model settings
groq_settings = GroqModelSettings(
    temperature=0.7,
    max_tokens=500,
    top_p=0.95,
    frequency_penalty=0,
)

# openai_settings = OpenAIModelSettings(
#     temperature=0.7,
#     max_tokens=500,
#     top_p=0.95,
#     frequency_penalty=0,
# )

# Initialize Groq model
visu_model = GroqModel(
    model_name=visu_model_name,
    provider=GroqProvider(api_key=settings.groq_key)
)

# visu_model = OpenAIModel(
#     model_name=visu_model_name,
#     provider=OpenAIProvider(api_key=settings.openai_key)
# )

emotion_model = GroqModel(   
    model_name=emotion_model_name,
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
    model=visu_model,
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
    output_type=emotion,
)

# @VISU.tool_plain(retries = 1)
async def wave_hand() -> str:
    """
        Tool to wave at the user, suggested to use when the user is greeting or saying goodbyes.
        Args : None
        Returns : str
    """
    print("Waving hand...")
    send_number_to_rpi(2)
    return "Success!"