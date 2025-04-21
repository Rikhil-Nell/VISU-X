# VISU-X: Multimodal AI Humanoid Assistant

VISU-X is an advanced conversational AI humanoid assistant designed to interact with users in a professional, engaging, and context-aware manner. It leverages cutting-edge technologies for speech-to-text (STT), text-to-speech (TTS), emotion detection, face recognition, and conversational memory to provide a seamless and human-like interaction experience.

---

## Features

### Core Functionality

1. **Conversational Agent**:
    * Powered by `pydantic_ai` and Groq's **Llama 3.3 70B Versatile** model for natural language understanding and generation.
    * Context-aware responses with a system prompt that ensures concise and professional communication.
2. **Emotion Detection**:
    * Dynamically detects user and bot emotions based on conversation history using Groq's LLM.
    * Updates the humanoid face's expression in real-time using **long polling**.
3. **Speech-to-Text (STT)**:
    * Uses **Groq's Whisper** for real-time transcription of user speech.
    * Integrated with `pyaudio` for audio capture and `webrtcvad` for voice activity detection (VAD).
4. **Text-to-Speech (TTS)**:
    * Converts bot responses into natural-sounding speech using **Deepgram**.
    * Uses `ffplay` for cross-platform audio playback.
5. **Humanoid Face Interaction**:
    * A dynamic front-end interface that visually represents the bot's emotions.
    * Real-time updates to facial expressions based on detected emotions via long polling.
6. **Memory System**:
    * Short-term memory for recent conversations.
    * Long-term memory using Supabase for persistent storage and retrieval of conversation history (potentially user-specific).
7. **Real-time User Identification (Face Tracking)**:
    * Utilizes `DeepFace` (with VGG-Face model) to identify registered users via webcam during voice interactions.
    * Runs asynchronously alongside the voice chat, allowing for personalized responses and memory management based on the recognized user.
8. **Logging and Monitoring**:
    * Integrated with Logfire for real-time logging and monitoring of system events.

---

## Project Structure

```bash

VISU-X/
├── app.py              # Streamlit-based front-end for text interaction
├── main.py             # Main entry point for voice and text chat modes
├── VISU.py             # Core agent logic and initialization
├── DB.py               # Database handler for conversation memory
├── emotion.py          # Emotion detection and long polling logic
├── face_tracker.py     # Real-time user identification via webcam using DeepFace
├── STT.py              # Speech-to-text functionality using Groq's Whisper
├── TTS.py              # Text-to-speech functionality using Deepgram
├── server.py           # Backend server for handling API requests (like emotion polling)
├── templates/          # HTML templates for the front-end (if server.py serves HTML)
├── static/             # Static assets (CSS, JS) (if server.py serves static files)
├── db/                 # Database directory for DeepFace face recognition images
│   ├── user1_name/
│   │   └── user1_face.jpg
│   └── user2_name/
│       └── user2_face.jpg
├── prompt.txt          # System prompt for the conversational agent
├── face_emotion.txt    # Template for emotion detection prompt
├── settings.py         # Configuration and environment variable management
├── requirements.txt    # Python dependencies list
├── README.md           # Project documentation
└── .gitignore          # Git ignore file

```

---

## Setup Instructions

### 1. Install Dependencies

Ensure you have Python 3.13 or higher installed. Then, install the required dependencies using pip or your preferred package manager like uv:

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (ensure uv is installed)
uv sync
```

Note: face_tracker.py uses DeepFace and opencv-python. DeepFace relies on backend frameworks like TensorFlow, PyTorch, or others. Ensure you have a compatible backend installed if pip install deepface or uv sync doesn't handle it automatically based on your system setup. opencv-python should be included in requirements.txt.

### 2. Configure Environment Variables

Create a .env file in the root directory and set the following variables:

```bash
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DEEPGRAM_API_KEY=your_deepgram_api_key
# Add any other required API keys or settings
```

### 3. Set Up Face Recognition Database

* Create a directory named db in the root of the project.
* Inside db, create subdirectories named after each user you want to recognize (e.g., db/alice/, db/bob/). Usernames should be simple identifiers.
* Place one or more clear, front-facing images of each user inside their respective directory (e.g., db/alice/alice_face1.jpg). More images per user can improve accuracy.

### 4. Run the Backend Server (If Used)

If your server.py handles emotion polling or other API functions needed by main.py or app.py, start it:

```bash
python server.py
```

### 5. Run the Streamlit Front-End (Optional)

For text-based interaction and potentially viewing the emotion face:

```bash
streamlit run app.py
```

### 6. Run the Main Application

Start the main application. This will give you options for voice or text chat.

```bash
python main.py
```

(Face tracking will start automatically when you choose the voice chat option)

## Usage

### Text Chat

* Run streamlit run app.py (if available) or use the text chat option in main.py.
* Enter your message and receive responses.

### Voice Chat

* Run python main.py and select the voice chat option (usually '2').
* The system will initialize STT, TTS, and attempt to start the face tracker using your default webcam.
* Speak into your microphone. Your speech will be transcribed by Groq Whisper.
* Simultaneously, the face tracker will try to identify you based on the images in the db folder. The identified user ID (unknown_user if no match) will be printed in the console and can be used internally (e.g., for personalized memory).
* VISU-X processes your query using the LLM, considering conversation history (potentially filtered by the recognized user ID).
* The response is generated and spoken back using Deepgram TTS.
* Emotion detection runs in parallel, potentially updating a visual front*end via the backend server and long polling.
* Say "goodbye" to end the voice session. The face tracker will stop automatically.

### Emotion Updates

* If using the Streamlit front-end or another UI connected to server.py, it likely polls the server periodically to get the latest detected bot/user emotion.
* The visual representation (humanoid face) updates accordingly.

## Current Limitations

* **Embedding Costs**: External API calls for embedding generation (if used by memory system) may lead to increased costs at scale.
* **Monitoring Dashboards**: Logfire integration might be limited to live dashboards without custom setups.
* **Emotion Detection**: Emotion detection is limited to predefined categories and relies on LLM interpretation accuracy.
* **Polling Overhead**: Long polling for emotion updates introduces latency and server load compared to WebSockets.
* **Face Recognition Accuracy**: Face recognition performance depends heavily on lighting conditions, face angle, webcam quality, and the quality/quantity of images in the face database. May misidentify users or fail to detect faces.
* **Face Recognition Performance**: DeepFace analysis can be CPU/GPU intensive, potentially impacting overall system performance on lower-end hardware, even when run in a separate thread.

## Future Enhancements

* **Custom Monitoring Dashboards**: Implement advanced Logfire dashboards.
* **Enhanced Memory System**: Improve memory retrieval efficiency and add more robust multi-user session handling based on recognized faces.
* **WebSocket Reintroduction**: Replace long polling with WebSockets for real-time emotion updates to reduce latency and server load.
* **Advanced Face Interaction**: Add more dynamic facial expressions and animations.
* **Multi-Persona Support**: Allow dynamic persona switching.
* **Improved Face Recognition**: Integrate more lightweight or robust models, potentially add face registration features via the UI. Handle scenarios with multiple people visible.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file (if one exists) for details.

## Acknowledgments

* Groq for Whisper STT and Llama 3.3 70B LLM access.
* Deepgram for TTS capabilities.
* Supabase for database integration (if used for long-term memory).
* Logfire for real-time logging and monitoring.
* DeepFace library for facial recognition capabilities.
* Libraries like pydantic_ai, asyncio, pyaudio, webrtcvad, streamlit, etc.
