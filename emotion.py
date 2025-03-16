import websockets
import json
from VISU import Deps, emotion_agent
from DB import DatabaseHandler

# Initialize dependencies and handlers
deps = Deps()
db_handler = DatabaseHandler(deps=deps)

WEBSOCKET_URL = "ws://localhost:8765"
MESSAGE_LIMIT = 5


async def set_face_emotion(emotion: str) -> None:
    """
    Sends the detected emotion to the WebSocket server to update the emotion display.

    Args:
        emotion (str): The detected emotion to be sent to the WebSocket server.
    """
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        payload = {"emotion": emotion}
        await websocket.send(json.dumps(payload))


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
    with open("face_emotion.txt", "r") as file:
        prompt_template = file.read()

    messages = await db_handler.get_memory(user_id, limit=MESSAGE_LIMIT)

    # Format the prompt with the recent message history
    response = await emotion_agent.run(user_prompt=prompt_template, message_history=messages)

    # Extract emotion and trigger WebSocket message
    emotion = response.data if response else "neutral"
    await set_face_emotion(emotion)

    return emotion
