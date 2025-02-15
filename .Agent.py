# Commenting redundant dependencies
# import tempfile  # Not used currently
# from pathlib import Path  # Not used currently
# import shutil  # Not used currently
# import time  # Not used currently
# import re  # Not used currently

import os
from dataclasses import dataclass
from typing import Any, List, Dict, Union
import json
from dotenv import load_dotenv

import httpx
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, UserPromptPart, TextPart
from supabase import create_client
from openai import OpenAI

# Load environment variables
load_dotenv()

# Setting up the model to use for inference
llm = 'llama-3.3-70b-versatile'

model = GroqModel(
    llm,
    api_key=os.getenv("GROQ_API_KEY"),
    # base_url=os.getenv("GROQ_BASE_URL")
)

# Setting Dependencies for the tools the agent uses
@dataclass
class Deps:
    supabase_url: str = os.getenv("SUPABASE_URL")
    supabase_key: str = os.getenv("SUPABASE_KEY")
    supabase_client: Any = create_client(supabase_url, supabase_key)

# Loading the Static Prompt
with open('prompt.txt', 'r') as file:
    static_system_prompt = file.read()

# Defining the Agent
VISU = Agent(
    model=model,
    system_prompt=static_system_prompt,
    deps_type=Deps,
    retries=2,
)

async def get_text_embedding(user_input: str) -> List[float]:
    
    try: 
        # Client for getting embeddings
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Generate embedding
        response = client.embeddings.create(input=user_input, model="text-embedding-3-small")

        embedding = response.data[0].embedding

        return embedding
    
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

@VISU.system_prompt(dynamic=True)
async def get_user_bot_emotion(ctx: RunContext[Deps]) -> str:
    """
    Dynamically detects the user's and bot's emotional state based on conversation history
    using a Groq API call, and updates the system prompt accordingly.
    """
    # Read the emotion analysis template from a file
    try:
        with open('emotion_analysis_prompt.txt', 'r') as file:
            prompt_template = file.read()
    except FileNotFoundError:
        print("Error: 'emotion_analysis_prompt.txt' not found.")
        return "user_emotion = neutral bot_emotion = focused"  # Default fallback

    # Prepare conversation history (up to the last 5 messages)
    message_history = '\n'.join(
        f"{message.kind}: {message.content}"
        for message in ctx.messages[-5:]
    )

    # Format the prompt with the recent message history
    prompt = prompt_template.format(message_history=message_history)

    # Make the API call to Groq
    try:
        response = await ctx.model(prompt)  # Direct call to the GroqModel LLM
    except Exception as e:
        print(f"Error during Groq API call: {e}")
        return "user_emotion = neutral bot_emotion = focused"  # Default fallback

    # Parse the Groq response to extract emotions
    try:
        response_data = json.loads(response.content)  # GroqModel outputs JSON
        user_emotion = response_data.get('user_emotion', 'neutral')
        bot_emotion = response_data.get('bot_emotion', 'focused')
        return f"user_emotion = {user_emotion} bot_emotion = {bot_emotion}"
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing Groq response: {e}")
        return "user_emotion = neutral bot_emotion = focused"  # Default fallback

 

# Vector Search Tool Implementation
# VISU.tool
async def vector_search(ctx: RunContext[Deps], deps : Deps, user_id: str, content: str, top_k: int = 5, ) -> List[ModelMessage]:
    
    # Generate the query embedding
    query_embedding = await get_text_embedding(user_input=content)

    # Build the query for vector similarity search
    query = f"""
        SELECT role, content
        FROM memory
        WHERE user_id = %s
        ORDER BY embedding <=> %s
        LIMIT %s;
    """

    supabase = deps.supabase_client

    # Execute the query
    response = supabase.table("memory").select("*").execute_sql(
        query, 
        [user_id, query_embedding, top_k]
    )

    if not response.data:
        return []  # Return an empty list if no results are found

    # Reverse results to maintain chronological order
    response = list(reversed(response.data))

    # Process the response into ModelMessage objects
    messages: List[ModelMessage] = []
    for item in response:
        role = item['role']
        content = item['content']

        if role == 'user':
            messages.append(
                ModelRequest(parts=[UserPromptPart(content=content)])
            )
        elif role == 'bot':
            messages.append(
                ModelResponse(parts=[TextPart(content=content)])
            )
    
    return messages


# Sliding Message History Retrieval
async def get_memory(deps: Deps, user_id: str, limit: int) -> List[ModelMessage]:
    
    supabase = deps.supabase_client

    # Fetch the latest messages from Supabase
    response = supabase.table('memory').select('role, content').eq('user_id', user_id).order('timestamp', desc=True).limit(limit).execute()
    response = list(reversed(response.data))  # Reverse for chronological order

    messages: List[ModelMessage] = []
    for item in response:
        role = item['role']
        content = item['content']

        if role == 'user':
            messages.append(
                ModelRequest(parts=[UserPromptPart(content=content)])
            )
        elif role == 'bot':
            messages.append(
                ModelResponse(parts=[TextPart(content=content)])
            )
    
    return messages

# Append a message to Supabase
async def append_message(deps: Deps, user_id: str, role: str, content: str) -> None:

    supabase_client = deps.supabase_client

    embedding = await get_text_embedding(user_input=content)

    supabase_client.table('memory').insert({
        'user_id': user_id,
        'role': role,
        'content': content,
        'embedding': embedding
    }).execute()


async def bot_emotion(deps: Deps, user_id: str) -> str:
    """
    Dynamically detects the user's and bot's emotional state based on conversation history
    using a Groq API call, and updates the system prompt accordingly.
    """
    # Read the emotion analysis template from a file
    with open('face_emotion.txt', 'r') as file:
        prompt_template = file.read()
    
    messages = await get_memory(deps, user_id, limit=5)

    message_history: List[ModelMessage] = []
    
    for message in messages:
        if isinstance(message, ModelRequest):
            # Extract the user message
            message_history.append(message)

        elif isinstance(message, ModelResponse):
            # Extract the bot message
            message_history.append(message)
    

    # Format the prompt with the recent message history
    Emotion_agent = Agent(
        model=model,
        deps_type=Deps,
        retries=2,
    )

    response = await Emotion_agent.run(user_prompt=prompt_template, message_history=message_history)

    # Extract emotion and trigger frontend API call
    async def set_face_emotion(emotion: str):
        async with httpx.AsyncClient() as client:
            frontend_url = "http://172.19.98.166:5000"  # Update with your frontend's endpoint
            payload = {"emotion": emotion}
            try:
                resp = await client.post(frontend_url, json=payload)
                if resp.status_code == 200:
                    print(f"Frontend updated with emotion: {emotion}")
                else:
                    print(f"Failed to update frontend: {resp.status_code}, {resp.text}")
            except Exception as e:
                print(f"Error updating frontend: {str(e)}")

    match response.data:
        case "focused":
            await set_face_emotion("focused")
            return "focused"
        case "happy":
            await set_face_emotion("happy")
            return "happy"
        case "sad":
            await set_face_emotion("sad")
            return "sad"
        case "confused":
            await set_face_emotion("confused")
            return "confused"
        case "angry":
            await set_face_emotion("angry")
            return "angry"
        case _:
            await set_face_emotion("neutral")
            return "neutral"
