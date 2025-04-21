from deepgram import (
    DeepgramClient,
    SpeakOptions,
)
import subprocess
from settings import Settings

settings = Settings()

filename = "audio/output_file.mp3"


def tts(input_text: str) -> None:
    SPEAK_OPTIONS = {"text": input_text}

    deepgram = DeepgramClient(api_key=settings.deepgram_key)

    options = SpeakOptions(
        model="aura-perseus-en",
    )

    deepgram.speak.rest.v("1").save(filename, SPEAK_OPTIONS, options)


def play() -> None:
    filename = "audio/output_file.mp3"
    subprocess.run(
        ["ffplay", "-nodisp", "-autoexit", filename],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
