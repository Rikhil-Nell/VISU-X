import asyncio
from VISU import VISU, Deps
from DB import DatabaseHandler
from emotion import bot_emotion
from TTS import tts, play

deps = Deps()
db_handler = DatabaseHandler(deps=deps)
user_id = "example_user_id"

while True:
    user_message = input("You: ")

    if user_message == "exit":
        break

    emotion = asyncio.run(bot_emotion(user_id=user_id))
    print("Detected Emotion:", emotion)

    asyncio.run(
        db_handler.append_message(user_id=user_id, role="user", content=user_message)
    )
    memory = asyncio.run(db_handler.get_memory(user_id=user_id, limit=20))

    result = asyncio.run(VISU.run(user_prompt=user_message, message_history=memory))
    response = result.data if result else "Sorry, I failed to process that."

    print("Bot:", response)

    tts(response)
    play()
    asyncio.run(
        db_handler.append_message(user_id=user_id, role="bot", content=response)
    )
