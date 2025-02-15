from VISU import Deps, VISU
from DB import DatabaseHandler
import httpx
from typing import List

# Initialize dependencies and handlers
deps = Deps()
db_handler = DatabaseHandler(deps=deps)

FRONTEND_URL = "http://172.19.98.166:5000"  # Update with your frontend's endpoint
MESSAGE_LIMIT = 5

async def set_face_emotion(emotion: str) -> None:
    """
    Sends the detected emotion to the frontend to update the emotion display.

    Args:
        emotion (str): The detected emotion to be sent to the frontend.
    """
    async with httpx.AsyncClient() as client:
        payload = {"emotion": emotion}
        try:
            resp = await client.post(FRONTEND_URL, json=payload)
            if resp.status_code == 200:
                print(f"Frontend updated with emotion: {emotion}")
            else:
                print(f"Failed to update frontend: {resp.status_code}, {resp.text}")
        except Exception as e:
            print(f"Error updating frontend: {str(e)}")

async def bot_emotion(user_id: str) -> str:
    """
    Dynamically detects the user's and bot's emotional state based on conversation history
    using a Groq API call, and updates the system prompt accordingly.

    Args:
        user_id (str): The ID of the user whose conversation history is being analyzed.

    Returns:
        str: The detected emotion.
    """
    # Read the emotion analysis template from a file
    with open('face_emotion.txt', 'r') as file:
        prompt_template = file.read()
    
    messages = await db_handler.get_memory(user_id, limit=MESSAGE_LIMIT)
    
    # Format the prompt with the recent message history
    response = await VISU.run(user_prompt=prompt_template, message_history=messages)

    # Extract emotion and trigger frontend API call
    emotion = response.data if response else "neutral"
#    await set_face_emotion(emotion)
    
    return emotion