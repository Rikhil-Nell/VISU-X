import asyncio
from VISU import VISU, Deps
from DB import DatabaseHandler
from emotion import convo_emotion
from STT import transcribe_audio
from TTS import tts, play
from pi_serial import send_number_to_rpi
from pydantic_ai.messages import ModelMessage, ToolCallPart, ToolReturnPart
from typing import List

deps = Deps()
database_handler = DatabaseHandler(deps=deps)

Tool_History : List[ModelMessage] = []

def get_user_id():
    try:
        with open("user_id.txt", "r") as f:
            return f.read().strip()
    except Exception:
        return "Unknown"

async def voice():
    listening = True  # Enable STT by default

    # Loop indefinitely until "goodbye" is detected
    while True:
        listening = True  # Enable STT
        # Start the transcription process
        transcription_response = transcribe_audio(listening)

        user_message = transcription_response

        # Infering the Speaker's identity
        # user_id = get_current_user()
        # print(f"[INFO] Active user: {user_id}")
        user_id = get_user_id()
        print(f"[INFO] Active user: {user_id}")
        
        if any(greet in user_message.lower() for greet in ["hey", "hello", "hi", "how are you", "greetings", "bye", "goodbye", "see you later"]):
            send_number_to_rpi(number=2)

        # Detect user's emotion and update the frontend
        bot_emotion, user_emotion = await convo_emotion(cur_user_prompt=user_message, user_id=user_id)
        print("Detected Bot Emotion:", bot_emotion)
        print("Detected User Emotion:", user_emotion)

        # Retrieve conversation memory
        memory = await database_handler.get_memory(user_id=user_id, limit=20)

        # Append user's message to the database
        await database_handler.append_message(user_id, "user", user_message)

        # Generate VISU's response
        result = await VISU.run(user_prompt=user_message, message_history=memory)
        bot_response = result.output if result else "Sorry, I couldn't process that."
        print("Recieived response:", bot_response)
        
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
    user_id = "Debug" # In text chat, face tracking isn't active

    while True:
        user_message = input("You: ")

        if user_message == "exit":
            break

        if any(greet in user_message.lower() for greet in ["hey", "hello", "hi", "how are you", "greetings", "bye", "goodbye", "see you later"]):
            send_number_to_rpi(number=2)

        bot_emotion, user_emotion = await convo_emotion(cur_user_prompt=user_message, user_id=user_id)
        print("Detected Bot Emotion:", bot_emotion)
        print("Detected User Emotion:", user_emotion)

        await database_handler.append_message(
            user_id=user_id, role="user", content=user_message
        )

        memory = await database_handler.get_memory(user_id=user_id, limit=20)

        result = await VISU.run(user_prompt=user_message, message_history=memory)
        response = result.output if result else "Sorry, I failed to process that."

        print("Bot:", response)

        await database_handler.append_message(
            user_id=user_id, role="bot", content=response
        )

# NEW main async function to manage tasks
async def main():
    print("Choose an option:")
    print("1. Text chat")
    print("2. Voice chat")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        await chat()
    elif choice == "2":
        await voice()


if __name__ == "__main__":
    # Run the main async function which handles task creation
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting application.")