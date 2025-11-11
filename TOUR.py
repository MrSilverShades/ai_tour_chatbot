import streamlit as st
import os
import google.generativeai as genai

# --- Page Configuration ---
# The title and icon that appear in the browser tab.
st.set_page_config(
    page_title="AI Tour Planner",
    page_icon="🗺️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- API Key and Model Setup ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- THIS IS THE SYSTEM INSTRUCTION ---
# Define the "personality" and rules for your bot.
SYSTEM_INSTRUCTION = """You are an AI tour planning assistant.
Your one and only job is to generate a travel itinerary based on the user's initial details (destination, duration, interests, style) and then answer follow-up questions to modify or elaborate on *that specific itinerary*.
You MUST NOT answer any general knowledge questions, questions about people, celebrities, history, math, or anything else unrelated to the user's travel plan.
If the user asks an unrelated question, you MUST politely decline and remind them you are only here to help with their trip.
For example, if the user asks "Who is the president?" or "What is 2+2?", you should say: "I'm sorry, but I can only help you with planning and modifying your travel itinerary."
"""
# --- END OF SYSTEM INSTRUCTION ---

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # --- THIS IS THE CHANGED LINE ---
    # Pass the new instruction to the model when you initialize it
    # I am using 'gemini-2.0-flash' as it is a modern, valid model.
    model = genai.GenerativeModel(
        'gemini-2.0-flash',
        system_instruction=SYSTEM_INSTRUCTION
    )
    # --- END OF CHANGED LINE ---
else:
    st.warning("Gemini API key not found. Please set it as a Streamlit secret or environment variable named 'GEMINI_API_KEY'.", icon="⚠️")
    model = None


# --- Chat History Management ---
# Use the format expected by the genai model: list of dicts
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Helper Functions ---
def get_gemini_response(question, chat_history):
    """
    Sends the user's question and chat history to the Gemini API
    and returns the model's response as a stream.
    Updates the session state history.
    """
    if not model:
        yield "Error: Gemini model is not initialized. Please check your API key."
        return

    try:
        # Pass the existing history to the model
        chat_session = model.start_chat(history=chat_history)
        
        # Send the new question
        response = chat_session.send_message(question, stream=True)
        
        full_response_text = ""
        for chunk in response:
            # Check for empty chunks or potential errors
            if hasattr(chunk, 'text'):
                chunk_text = chunk.text
                full_response_text += chunk_text
                yield chunk_text
            else:
                # Handle potential non-text parts or empty responses gracefully
                pass
            
        # Manually add the user question and full model response to the session state history
        # This is critical for the model to have context for follow-up questions
        st.session_state.chat_history.append({"role": "user", "parts": [question]})
        st.session_state.chat_history.append({"role": "model", "parts": [full_response_text]})

    except Exception as e:
        st.error(f"An error occurred with the Gemini API: {e}")
        yield f"Sorry, I encountered an error: {e}"

# --- Streamlit App UI ---

# Sidebar for user inputs and controls
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/googlelogo/svg/googlelogo_clr_74x24px.svg", width=100)
    st.header("✨ Plan Your Perfect Trip")
    st.write("Fill in the details below and let AI be your travel guide.")

    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")

    destination = st.text_input("📍 **Destination**", placeholder="e.g., Paris, France")
    duration = st.number_input("⏳ **Duration (in days)**", min_value=1, max_value=30, value=7, step=1)
    interests = st.text_area("🎨 **Interests & Preferences**", placeholder="e.g., historical sites, culinary experiences, hiking...")
    style = st.selectbox(
        "✈️ **Travel Style**",
        ["Balanced", "Relaxed", "Fast-Paced", "Family-Friendly", "Luxury", "Budget-Conscious"]
    )

    generate_plan = st.button("Generate Itinerary", use_container_width=True, type="primary")

    st.markdown("---")
    st.info("This AI Tour Planner is powered by Google Gemini.")

# Main panel for the chat interface
st.title("🗺️ AI-Powered Tour Planner")
st.markdown("### Your personal guide to crafting unforgettable journeys.")

# Display initial welcome message if chat history is empty
if not st.session_state.chat_history:
    st.info("Start by entering your trip details in the sidebar and click 'Generate Itinerary'.")

# Display previous messages from chat history
for message in st.session_state.chat_history:
    # Convert role 'model' to 'assistant' for st.chat_message
    role = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role):
        st.markdown(message["parts"][0])

# Logic to handle itinerary generation
if generate_plan:
    if not destination or not interests:
        st.warning("Please fill in the **Destination** and your **Interests**.", icon="✍️")
    elif not model:
        st.error("Cannot generate plan. Gemini API key is not configured.", icon="🚫")
    else:
        # Clear old history before starting a new plan
        st.session_state.chat_history = []
        
        # This is the formatted message the user sees
        initial_prompt_display = f"""
        **Planning a trip with the following details:**
        - **Destination:** {destination}
        - **Duration:** {duration} days
        - **Interests:** {interests}
        - **Travel Style:** {style}
        """
        
        # This is the detailed prompt the AI receives
        model_prompt = f"Plan a {duration}-day trip to {destination} for a traveler with interests in {interests} and a {style} travel style. Create a detailed, day-by-day itinerary. Make it engaging and easy to read. Use Markdown for formatting (like bolding and bullet points)."

        # Display the user's formatted request in the chat
        with st.chat_message("user"):
            st.markdown(initial_prompt_display)
        
        with st.spinner("🚀 Crafting your personalized adventure..."):
            with st.chat_message("assistant"):
                # Pass the model_prompt and an EMPTY history to start
                response_generator = get_gemini_response(model_prompt, [])
                st.write_stream(response_generator)
        
        # Rerun to ensure the chat history (updated in the function) is displayed
        st.rerun()


# Handle follow-up questions
if user_query := st.chat_input("Ask for changes or more details..."):
    if not st.session_state.chat_history:
        st.warning("Please generate an itinerary first.", icon="🗺️")
    elif not model:
        st.error("Cannot process your request. Gemini API key is not configured.", icon="🚫")
    else:
        # Display the user's new message
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.spinner("🤔 Thinking..."):
            with st.chat_message("assistant"):
                # Pass the new query and the *existing* history
                response_generator = get_gemini_response(user_query, st.session_state.chat_history)
                st.write_stream(response_generator)
        
        # Rerun to display the new messages that were added to history
        st.rerun()