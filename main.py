import asyncio
from VISU import VISU, Deps
from DB import DatabaseHandler
from emotion import bot_emotion
from STT import transcribe_audio
from TTS import tts, play

# Initialize dependencies and handlers
deps = Deps()
database_handler = DatabaseHandler(deps=deps)


async def main():

    # Loop indefinitely until "goodbye" is detected
    while True:

        # Start the transcription process
        transcription_response = transcribe_audio()
        
        if transcription_response == "goodbye":
            break

        # Process the transcription response
        user_id = "example_user_id"  # Replace with actual user ID
        user_message = str(transcription_response)

        # Detect user's emotion and update the frontend
        emotion = await bot_emotion(user_id)
        print(f"Detected Emotion: {emotion}")

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

        # Play the TTS audio
        play()

        # Reset transcription_response for the next loop iteration
        transcription_response = ""


if __name__ == "__main__":
    asyncio.run(main())
