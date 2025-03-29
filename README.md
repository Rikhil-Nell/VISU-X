# VISU-X: Multimodal AI Humanoid Assistant

VISU-X is an advanced conversational AI humanoid assistant designed to interact with users in a professional, engaging, and context-aware manner. It leverages cutting-edge technologies for speech-to-text (STT), text-to-speech (TTS), emotion detection, and conversational memory to provide a seamless and human-like interaction experience.

---

## Features

### Core Functionality
1. **Conversational Agent**:
   - Powered by `pydantic_ai` and Groq's **Llama 3.3 70B Versatile** model for natural language understanding and generation.
   - Context-aware responses with a system prompt that ensures concise and professional communication.

2. **Emotion Detection**:
   - Dynamically detects user and bot emotions based on conversation history using Groq's LLM.
   - Updates the humanoid face's expression in real-time using **long polling**.

3. **Speech-to-Text (STT)**:
   - Uses **Groq's Whisper** for real-time transcription of user speech.
   - Integrated with `pyaudio` for audio capture and `webrtcvad` for voice activity detection (VAD).

4. **Text-to-Speech (TTS)**:
   - Converts bot responses into natural-sounding speech using **Deepgram**.
   - Uses `ffplay` for cross-platform audio playback.

5. **Humanoid Face Interaction**:
   - A dynamic front-end interface that visually represents the bot's emotions.
   - Real-time updates to facial expressions based on detected emotions via long polling.

6. **Memory System**:
   - Short-term memory for recent conversations.
   - Long-term memory using Supabase for persistent storage and retrieval of conversation history.

7. **Logging and Monitoring**:
   - Integrated with Logfire for real-time logging and monitoring of system events.

---

## Project Structure

```
VISU-X/
├── app.py               # Streamlit-based front-end for text interaction
├── main.py              # Main entry point for voice and text chat modes
├── VISU.py              # Core agent logic and initialization
├── DB.py                # Database handler for conversation memory
├── emotion.py           # Emotion detection and long polling logic
├── STT.py               # Speech-to-text functionality using Groq's Whisper
├── TTS.py               # Text-to-speech functionality using Deepgram
├── server.py            # Backend server for handling API requests
├── templates/           # HTML templates for the front-end
├── static/              # Static assets (CSS, JS)
├── prompt.txt           # System prompt for the conversational agent
├── face_emotion.txt     # Template for emotion detection
├── settings.py          # Configuration and environment variable management
├── README.md            # Project documentation
└── .gitignore           # Git ignore file
```

---

## Setup Instructions

### 1. Install Dependencies
Ensure you have Python 3.13 or higher installed. Then, install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory and set the following variables:
```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DEEPGRAM_API_KEY=your_deepgram_api_key
```

### 3. Run the Backend Server
Start the backend server to handle API requests and long polling:
```bash
python server.py
```

### 4. Run the Streamlit Front-End
Launch the Streamlit-based front-end for text-based interaction:
```bash
streamlit run app.py
```

### 5. Run the Main Application
Start the main application for voice or text chat:
```bash
python main.py
```

---

## Usage

### Text Chat
1. Select "Chat with VISU" in the Streamlit interface.
2. Enter your message in the input field and receive a response from VISU.
3. Click the "Play Response" button to hear the bot's response.

### Voice Chat
1. Run the `main.py` script and select the voice chat option.
2. Speak into your microphone, and VISU will transcribe, process, and respond to your queries using Groq's Whisper.
3. Say "goodbye" to end the session.

### Emotion Updates
- The front-end polls the backend server at regular intervals to fetch the latest detected emotion.
- The humanoid face updates its expression based on the fetched emotion.

---

## Current Limitations
- **Embedding Costs**: External API calls for embedding generation may lead to increased costs at scale.
- **Monitoring Dashboards**: Logfire integration is limited to live dashboards; custom dashboards are yet to be implemented.
- **Emotion Detection**: Emotion detection is limited to predefined categories.
- **Polling Overhead**: Long polling introduces additional latency and server load compared to WebSockets.

---

## Future Enhancements
1. **Custom Monitoring Dashboards**:
   - Implement advanced Logfire dashboards for better monitoring and analytics.

2. **Enhanced Memory System**:
   - Improve memory retrieval efficiency and add support for multi-user sessions.

3. **WebSocket Reintroduction**:
   - Reintroduce WebSocket-based communication for real-time updates to reduce latency and server load.

4. **Advanced Face Interaction**:
   - Add more dynamic facial expressions and animations for a richer user experience.

5. **Multi-Persona Support**:
   - Allow users to select different personas for VISU based on their preferences.

---

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments
- **Groq** for providing the Whisper STT and Llama 3.3 70B Versatile model.
- **Deepgram** for TTS capabilities.
- **Supabase** for database integration.
- **Logfire** for real-time logging and monitoring.