import webrtcvad
import pyaudio
import sys
import time
import wave
from uuid import uuid4
from groq import Groq
from settings import Settings

# Move constant declarations outside the function
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 8000, 16000, 32000
FRAMES_PER_BUFFER = 320

# Initialize Settings (outside the function)
settings = Settings()

# Initialize the Groq Client (outside the function)
client = Groq(api_key=settings.groq_key)

# Initialize the VAD with a mode (e.g. aggressive, moderate, or gentle) (outside the function)
vad = webrtcvad.Vad(1)

# Initialize PyAudio (outside the function)
pa = pyaudio.PyAudio()

def transcribe_audio() -> str:
    print("Voice Activity Monitoring")
    print("1 - Activity Detected")
    print("_ - No Activity Detected")
    print("X - No Activity Detected for Last IDLE_TIME Seconds")
    print("\nMonitor Voice Activity Below:")

    # Open a PyAudio stream to get audio data from the microphone
    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER,
    )

    inactive_session = False
    inactive_since = time.time()
    frames = []  # list to hold audio frames
    while True:
        # Read audio data from the microphone
        data = stream.read(FRAMES_PER_BUFFER)

        # Check if the audio is active (i.e. contains speech)
        is_active = vad.is_speech(data, sample_rate=RATE)

        # Check Flagging for Stop after N Seconds
        idle_time = 1
        if is_active:
            inactive_session = False
        else:
            if inactive_session == False:
                inactive_session = True
                inactive_since = time.time()
            else:
                inactive_session = True

        # Stop hearing if no voice activity detected for N Seconds
        if (inactive_session == True) and (time.time() - inactive_since) > idle_time:
            sys.stdout.write("X")

            # Append data chunk of audio to frames - save later
            frames.append(data)

            # Save the recorded data as a WAV file
            filename = (
                f"audio/RECORDED-{str(time.time())}-{str(uuid4()).replace('-', '')}.wav"
            )
            wf = wave.open(filename, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pa.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
            wf.close()

            with open(filename, "rb") as file:
                # Create a transcription of the audio file
                transcription = client.audio.transcriptions.create(
                    file=(filename, file.read()),  # Required audio file
                    model="whisper-large-v3-turbo",  # Required model to use for transcription
                )
            # print(f"Transcription: {transcription.text}")

            # Close the PyAudio stream
            stream.stop_stream()
            stream.close()

            # Return the transcription text
            return transcription.text

        else:
            sys.stdout.write("1" if is_active else "_")

        # Append data chunk of audio to frames - save later
        frames.append(data)

        # Flush Terminal
        sys.stdout.flush()

# Example usage:
# transcription = transcribe_audio()
# print(transcription)