from deepgram import (
    DeepgramClient,
    SpeakOptions,
)
import os
import streamlit as st
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


def play(filename: str) -> None:
    subprocess.Popen(
        ["ffplay", "-nodisp", "-autoexit", filename],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def play_st() -> None:
    with open("audio/output_file.mp3", "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/mp3")
