import streamlit as st
import os
import json
from datetime import datetime
import google.generativeai as genai

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Tour Planner Pro",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- API Key and Model Setup ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# System instruction
SYSTEM_INSTRUCTION = """You are an expert AI tour planning assistant with deep knowledge of global destinations, local cultures, and travel logistics.

Your responsibilities:
1. Generate personalized, detailed day-by-day travel itineraries
2. Provide local insights, hidden gems, and cultural tips
3. Answer questions about accommodations, transportation, budget estimates, and activities
4. Suggest alternatives and modifications to the itinerary
5. Offer weather considerations and packing advice
6. Recommend local cuisine and dining experiences
7. Provide safety tips and cultural etiquette advice

Format your responses with:
- Clear day-by-day structure with emojis
- Specific activity times and durations
- Estimated costs (when relevant)
- Transportation details between locations
- Restaurant and accommodation suggestions
- Cultural insights and local tips

You MUST stay focused on travel planning. Politely decline unrelated questions."""

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=SYSTEM_INSTRUCTION)
else:
    st.error("⚠️ Gemini API key not found. Please configure it in secrets or environment variables.", icon="🚫")
    model = None

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "saved_itineraries" not in st.session_state:
    st.session_state.saved_itineraries = []

if "current_trip" not in st.session_state:
    st.session_state.current_trip = None

if "trip_stats" not in st.session_state:
    st.session_state.trip_stats = {
        "total_trips": 0,
        "total_days": 0,
        "destinations": []
    }

# --- Helper Functions ---
def get_gemini_response(question, chat_history):
    """Enhanced response generator with error handling"""
    if not model:
        yield "❌ Error: Gemini model is not initialized. Please check your API key."
        return
    
    try:
        chat_session = model.start_chat(history=chat_history)
        response = chat_session.send_message(question, stream=True)
        full_response_text = ""
        
        for chunk in response:
            if hasattr(chunk, 'text'):
                chunk_text = chunk.text
                full_response_text += chunk_text
                yield chunk_text
        
        st.session_state.chat_history.append({"role": "user", "parts": [question]})
        st.session_state.chat_history.append({"role": "model", "parts": [full_response_text]})
        
    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")
        yield f"Sorry, I encountered an error: {e}"

def save_itinerary(destination, duration, interests, style):
    """Save current itinerary to history"""
    itinerary = {
        "destination": destination,
        "duration": duration,
        "interests": interests,
        "style": style,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chat_history": st.session_state.chat_history.copy()
    }
    st.session_state.saved_itineraries.append(itinerary)
    st.success("✅ Itinerary saved successfully!")

def export_chat_history():
    """Export chat history as JSON"""
    export_data = {
        "trip_details": st.session_state.current_trip,
        "chat_history": st.session_state.chat_history,
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return json.dumps(export_data, indent=2)

def load_saved_itinerary(index):
    """Load a previously saved itinerary"""
    itinerary = st.session_state.saved_itineraries[index]
    st.session_state.chat_history = itinerary["chat_history"].copy()
    st.session_state.current_trip = {
        "destination": itinerary["destination"],
        "duration": itinerary["duration"],
        "interests": itinerary["interests"],
        "style": itinerary["style"]
    }

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("## ✈️ AI Tour Planner Pro")
    st.markdown("---")
    
    # Trip Planning Section
    with st.expander("🗺️ New Trip Planning", expanded=True):
        destination = st.text_input(
            "📍 Destination",
            placeholder="e.g., Tokyo, Japan",
            help="Enter your dream destination"
        )
        
        duration = st.slider(
            "⏳ Duration (days)",
            min_value=1,
            max_value=30,
            value=7,
            help="How many days will you be traveling?"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            budget = st.selectbox(
                "💰 Budget",
                ["Budget", "Mid-Range", "Luxury", "Ultra-Luxury"],
                help="Select your budget range",
                index=0
            )
        
        with col2:
            travelers = st.number_input(
                "👥 Travelers",
                min_value=1,
                max_value=20,
                value=2
            )
        
        # Interest options with FULL TEXT
        interest_options = [
            "🏛️ Historical Sites",
            "🌲 Nature & Wildlife",
            "🍜 Food & Cuisine",
            "🏄 Adventure Sports",
            "🏖️ Beaches",
            "🛍️ Shopping",
            "🎨 Art & Museums",
            "🌃 Nightlife",
            "📸 Photography",
            "🎭 Local Culture",
            "🧘 Wellness & Spa"
        ]
        
        interests = st.multiselect(
            "🎨 Select Your Interests",
            interest_options,
            default=["🎭 Local Culture"],
            help="Choose activities you're interested in"
        )
        
        additional_prefs = st.text_area(
            "✍️ Additional Preferences",
            placeholder="Any specific requirements or preferences...",
            height=100
        )
        
        style = st.selectbox(
            "✈️ Travel Pace",
            ["Balanced", "Relaxed", "Fast-Paced", "Family-Friendly"],
            help="Select your preferred travel pace",
            index=0
        )
        
        accommodation = st.selectbox(
            "🏨 Accommodation Type",
            ["Hotels", "Resorts", "Hostels", "Airbnb", "Boutique Hotels", "Mix"],
            help="Choose your preferred accommodation",
            index=0
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        generate_plan = st.button(
            "🚀 Generate Itinerary",
            use_container_width=True,
            type="primary"
        )
    
    st.markdown("---")
    
    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("💾 Save Trip", use_container_width=True):
            if st.session_state.current_trip:
                save_itinerary(
                    st.session_state.current_trip["destination"],
                    st.session_state.current_trip["duration"],
                    st.session_state.current_trip["interests"],
                    st.session_state.current_trip["style"]
                )
    
    # Export chat history
    if st.session_state.chat_history:
        export_data = export_chat_history()
        st.download_button(
            "📥 Export Chat",
            data=export_data,
            file_name=f"trip_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Saved Itineraries
    if st.session_state.saved_itineraries:
        with st.expander("📚 Saved Itineraries"):
            for idx, itinerary in enumerate(st.session_state.saved_itineraries):
                if st.button(
                    f"🗺️ {itinerary['destination']} ({itinerary['duration']} days)",
                    key=f"load_{idx}",
                    use_container_width=True
                ):
                    load_saved_itinerary(idx)
                    st.rerun()
    
    st.markdown("---")
    
    # Quick Actions
    with st.expander("⚡ Quick Actions"):
        quick_actions = [
            ("💡 Budget Activities", "Suggest budget-friendly activities"),
            ("🍽️ Local Restaurants", "Recommend local restaurants"),
            ("🏨 Accommodations", "Find accommodation options"),
            ("🚗 Transportation", "Plan transportation"),
            ("📸 Photo Spots", "Best photo spots"),
            ("🎒 Packing List", "Create packing list"),
            ("🌤️ Weather Info", "Weather considerations")
        ]
        
        for display_text, action_text in quick_actions:
            if st.button(display_text, use_container_width=True, key=f"quick_{action_text}"):
                st.session_state.quick_action = action_text
    
    st.markdown("---")
    st.caption("Powered by Google Gemini 2.0 Flash")

# --- Main Content Area ---
# Header Section
st.markdown("<h1>✈️ AI Tour Planner Pro</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your intelligent companion for unforgettable journeys</p>", unsafe_allow_html=True)

# Statistics Dashboard
if st.session_state.current_trip or st.session_state.trip_stats["total_trips"] > 0:
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Using st.metric for default styling
        st.metric(label="🗺️ Total Trips", value=st.session_state.trip_stats['total_trips'])
    
    with col2:
        st.metric(label="📅 Days Traveled", value=st.session_state.trip_stats['total_days'])
    
    with col3:
        st.metric(label="🌍 Destinations", value=len(st.session_state.trip_stats['destinations']))
    
    with col4:
        st.metric(label="💬 Messages", value=len(st.session_state.chat_history))


st.markdown("---")

# Welcome Message
if not st.session_state.chat_history:
    st.info("👋 **Welcome!** Fill in your trip details in the sidebar and click 'Generate Itinerary' to start planning!", icon="✨")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("<h3>🎯 Personalized Plans</h3>", unsafe_allow_html=True)
            st.markdown("<p>Get custom itineraries tailored to your interests, budget, and travel style with AI-powered recommendations.</p>", unsafe_allow_html=True)
    
    with col2:
        with st.container(border=True):
            st.markdown("<h3>💬 Interactive Chat</h3>", unsafe_allow_html=True)
            st.markdown("<p>Ask questions, request changes, and refine your itinerary through natural conversation with our AI assistant.</p>", unsafe_allow_html=True)
    
    with col3:
        with st.container(border=True):
            st.markdown("<h3>💾 Save & Export</h3>", unsafe_allow_html=True)
            st.markdown("<p>Save your favorite itineraries and export them as JSON files for offline access and easy sharing.</p>", unsafe_allow_html=True)

# Chat History Display
for idx, message in enumerate(st.session_state.chat_history):
    role = "assistant" if message["role"] == "model" else message["role"]
    avatar = "🤖" if role == "assistant" else "👤"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["parts"][0])
        
        # Add action buttons for last assistant message
        if role == "assistant" and idx == len(st.session_state.chat_history) - 1:
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("👍 Helpful", key=f"like_{idx}"):
                    st.toast("Thanks for your feedback!", icon="✅")
            with col2:
                if st.button("👎 Not Helpful", key=f"dislike_{idx}"):
                    st.toast("We'll improve!", icon="📝")

# Handle Itinerary Generation
if generate_plan:
    if not destination or not interests:
        st.warning("⚠️ Please fill in the **Destination** and select at least one **Interest**.", icon="✍️")
    elif not model:
        st.error("🚫 Cannot generate plan. Gemini API key is not configured.", icon="❌")
    else:
        # Clear old history
        st.session_state.chat_history = []
        
        # Store current trip details
        # Remove emojis from interests for clean storage
        clean_interests = [interest.split(" ", 1)[1] if " " in interest else interest for interest in interests]
        
        st.session_state.current_trip = {
            "destination": destination,
            "duration": duration,
            "interests": ", ".join(clean_interests),
            "style": style,
            "budget": budget,
            "travelers": travelers,
            "accommodation": accommodation
        }
        
        # Update statistics
        st.session_state.trip_stats["total_trips"] += 1
        st.session_state.trip_stats["total_days"] += duration
        if destination not in st.session_state.trip_stats["destinations"]:
            st.session_state.trip_stats["destinations"].append(destination)
        
        # Create user-visible prompt
        initial_prompt_display = f"""
**🗺️ Planning your {duration}-day adventure to {destination}!**

**Trip Details:**
- 📍 **Destination:** {destination}
- ⏳ **Duration:** {duration} days
- 💰 **Budget:** {budget}
- 👥 **Travelers:** {travelers} person(s)
- 🎨 **Interests:** {", ".join(clean_interests)}
- ✈️ **Travel Style:** {style}
- 🏨 **Accommodation:** {accommodation}
- ✍️ **Additional Preferences:** {additional_prefs if additional_prefs else "None"}
"""
        
        # Create detailed AI prompt
        model_prompt = f"""Plan a comprehensive {duration}-day trip to {destination} for {travelers} traveler(s) with a {budget} budget.

Travel Interests: {", ".join(clean_interests)}
Travel Style: {style}
Accommodation Preference: {accommodation}
Additional Preferences: {additional_prefs if additional_prefs else "None"}

Create a detailed day-by-day itinerary that includes:
1. Daily activities with specific timings
2. Recommended restaurants for each meal
3. Transportation options between locations
4. Estimated costs for activities and meals
5. Cultural tips and local insights
6. Hidden gems and local favorites
7. Best times to visit attractions
8. Photography opportunities
9. Weather considerations
10. Packing suggestions

Make it engaging, practical, and easy to follow. Use emojis and clear formatting."""

        # Display user request
        with st.chat_message("user", avatar="👤"):
            st.markdown(initial_prompt_display)
        
        # Generate and display response
        with st.spinner("🚀 Crafting your perfect itinerary... This may take a moment!"):
            with st.chat_message("assistant", avatar="🤖"):
                response_generator = get_gemini_response(model_prompt, [])
                st.write_stream(response_generator)
        
        st.rerun()

# Handle Follow-up Questions and Quick Actions
user_query = st.chat_input("💬 Ask questions, request changes, or add details...")

# Handle quick actions
if "quick_action" in st.session_state:
    user_query = st.session_state.quick_action
    del st.session_state.quick_action

if user_query:
    if not st.session_state.chat_history:
        st.warning("⚠️ Please generate an itinerary first before asking questions!", icon="🗺️")
    elif not model:
        st.error("🚫 Cannot process your request. Gemini API key is not configured.", icon="❌")
    else:
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)
        
        # Generate response
        with st.spinner("🤔 Processing your request..."):
            with st.chat_message("assistant", avatar="🤖"):
                response_generator = get_gemini_response(user_query, st.session_state.chat_history)
                st.write_stream(response_generator)
        
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #64748b;">
    <p style='font-size: 1.1rem; margin-bottom: 0.5rem;'>Made with ❤️ using Streamlit and Google Gemini 2.0 Flash</p>
    <p style='font-size: 0.9rem; color: #94a3b8;'>© 2025 AI Tour Planner Pro - Your intelligent travel companion</p>
</div>
""", unsafe_allow_html=True)