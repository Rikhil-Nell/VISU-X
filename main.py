import asyncio
from VISU import VISU, Deps
from DB import DatabaseHandler
from emotion import bot_emotion
from STT import transcribe_audio
from TTS import tts, play

# Initialize dependencies and handlers
deps = Deps()
database_handler = DatabaseHandler(deps=deps)

user_id = "example_user_id"  # Replace with actual user ID


async def voice():
    listening = True  # Enable STT by default

    # Loop indefinitely until "goodbye" is detected
    while True:
        listening = True  # Enable STT
        # Start the transcription process
        transcription_response = transcribe_audio(listening)

        user_message = transcription_response

        # Detect user's emotion and update the frontend
        emotion = await bot_emotion(user_id)
        print(f"\n Detected Emotion: {emotion}")

        # Retrieve conversation memory
        memory = await database_handler.get_memory(user_id=user_id, limit=20)

        # Append user's message to the database
        await database_handler.append_message(user_id, "user", user_message)

        # Generate VISU's response
        result = await VISU.run(user_prompt=user_message, message_history=memory)
        bot_response = result.data if result else "Sorry, I couldn't process that."

        # Append VISU's response to the database
        await database_handler.append_message(user_id, "bot", bot_response)

        # Generate TTS audio from VISU's response
        tts(bot_response)

        listening = False  # Disable STT while TTS is playing
        play()  # Blocking call ensures STT resumes only after TTS finishes
        listening = True  # Re-enable STT after playback

        if "goodbye" in transcription_response.lower():
            break  # Exit the loop if "goodbye" is detected

        transcription_response = ""  # Reset the transcription response


async def chat():
    while True:
        user_message = input("You: ")

        if user_message == "exit":
            break

        emotion = await bot_emotion(user_id=user_id)
        print("Detected Emotion:", emotion)

        await database_handler.append_message(
            user_id=user_id, role="user", content=user_message
        )

        memory = await database_handler.get_memory(user_id=user_id, limit=20)

        result = await VISU.run(user_prompt=user_message, message_history=memory)
        response = result.data if result else "Sorry, I failed to process that."

        print("Bot:", response)

        await database_handler.append_message(
            user_id=user_id, role="bot", content=response
        )


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Text chat")
    print("2. Voice chat")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        asyncio.run(chat())
    elif choice == "2":
        asyncio.run(voice())
