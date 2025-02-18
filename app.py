import streamlit as st
import asyncio
from VISU import VISU, Deps
from DB import DatabaseHandler
from emotion import bot_emotion 
from TTS import tts, play_st
# Initialize dependencies and handlers
deps = Deps()
db_handler = DatabaseHandler(deps=deps)

# Set Streamlit page configuration
st.set_page_config(
    page_title="VISU: Multimodal Robot Assistant",
    layout="wide",
    page_icon="🤖",
)

# Sidebar navigation
st.sidebar.header("Navigation")
selected_section = st.sidebar.radio("Select Section", ["Chat with VISU", "Logs", "Robot Movement"])

# Chat Section
if selected_section == "Chat with VISU":
    st.title("🤖 Chat with VISU")
    st.write("Interact with VISU in text or voice!")

    # Initialize session state for chat history and microphone state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mic_active" not in st.session_state:
        st.session_state.mic_active = False

    # Display chat history
    st.subheader("Chat History")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input field for user message
    user_message = st.chat_input("Ask VISU anything...")

    # Handle text input
    if user_message:
        # Append user's message to session state
        st.session_state.messages.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)

        # Mock user ID (replace with actual user ID)
        user_id = "example_user_id"

        # Detect user's emotion and update the frontend
        emotion = asyncio.run(bot_emotion(user_id))
        st.markdown(f"<h3 style='color:grey;'>Detected Emotion: {emotion}</h3>", unsafe_allow_html=True)
        
        # Append user's message to the database
        asyncio.run(db_handler.append_message(user_id, "user", user_message))
    
        # Retrieve conversation memory
        memory = asyncio.run(db_handler.get_memory(user_id=user_id, limit=20))

        # Generate VISU's response
        result = asyncio.run(VISU.run(user_prompt=user_message, message_history=memory))
        bot_response = result.data if result else "Sorry, I couldn't process that."
        
        # Generate TTS audio from VISU's response
        tts(bot_response)
        
        # Append VISU's response to session state and database
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        
        # Play the TTS audio
        st.button("🔊 Play Audio", on_click=play_st())
            
        asyncio.run(db_handler.append_message(user_id, "bot", bot_response))

# Logs Section
elif selected_section == "Logs":
    st.title("📜 Logs")
    st.write("This section displays live logs from Logfire for monitoring.")

    # Example of live log refresh (mock logs for now)
    log_data = ["[INFO] System initialized.", "[INFO] VISU response time: 0.5s", "[ERROR] Network timeout."]
    st.write("**Live Logs**:")
    for log in log_data:
        st.code(log)

# Robot Movement Section
elif selected_section == "Robot Movement":
    st.title("🚀 Robot Movement Dashboard")
    st.write(
        "Monitor and control VISU's movement. You can integrate live tracking "
        "visualizations here in the future."
    )

    # Placeholder for robot movement visualization
    st.text("Movement data goes here.")
    st.bar_chart({"Forward": 30, "Backward": 10, "Left": 15, "Right": 20})

# Footer
st.sidebar.write("---")
st.sidebar.markdown(
    "### Built with ❤️ by the VISU Development Team.\n\n"
    "For support, contact us at [email@example.com](mailto:email@example.com)."
)
