import asyncio
from VISU import VISU, Deps
from DB import DatabaseHandler
from emotion import bot_emotion
from STT import get_transcript
from TTS import tts, play

class ConversationManager:
    def __init__(self):
        self.transcription_response = ""
        self.database_handler = DatabaseHandler(deps=Deps())
        self.botemotion = bot_emotion

    async def main(self):
        def handle_full_sentence(full_sentence):
            self.transcription_response = full_sentence

        # Loop indefinitely until "goodbye" is detected
        while True:
            await get_transcript(handle_full_sentence)
            
            # Check for "goodbye" to exit the loop
            if "goodbye" in self.transcription_response.lower():
                break

            # Process the transcription response
            user_id = "example_user_id"  # Replace with actual user ID
            user_message = self.transcription_response

            # Detect user's emotion and update the frontend
            emotion = await self.botemotion(user_id)
            print(f"Detected Emotion: {emotion}")

            # Append user's message to the database
            await self.database_handler.append_message(user_id, "user", user_message)
        
            # Retrieve conversation memory
            memory = await self.database_handler.get_memory(user_id=user_id, limit=20)

            # Generate VISU's response
            result = await VISU.run(user_prompt=user_message, message_history=memory)
            bot_response = result.data if result else "Sorry, I couldn't process that."
            
            # Append VISU's response to the database
            await self.database_handler.append_message(user_id, "bot", bot_response)

            # Generate TTS audio from VISU's response
            tts(bot_response)
            
            # Play the TTS audio
            play("audio/output_file.mp3")

            # Reset transcription_response for the next loop iteration
            self.transcription_response = ""

if __name__ == "__main__":
    manager = ConversationManager()
    asyncio.run(manager.main())