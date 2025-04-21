import aiohttp
from VISU import Deps, emotion_agent
from DB import DatabaseHandler

# Initialize dependencies and handlers
deps = Deps()
db_handler = DatabaseHandler(deps=deps)

MESSAGE_LIMIT = 5

async def set_face_emotion(emotion):
    async with aiohttp.ClientSession() as session:
        await session.post("http://localhost:5000/api/express", json={"type": emotion})


async def convo_emotion(cur_user_prompt: str, user_id: str) -> str:
    
    prompt = f"User: {cur_user_prompt}"
    messages = await db_handler.get_memory(user_id, limit=MESSAGE_LIMIT)
    response = await emotion_agent.run(user_prompt=prompt, message_history=messages)
    bot_emotion = response.output.emotionofbot if response else "neutral"
    user_emotion = response.output.emotionofuser if response else "neutral"
    await set_face_emotion(bot_emotion)

    return bot_emotion, user_emotion
