# 🗺️ AI Tour Planner Chatbot

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.7+-blue?style=for-the-badge&logo=python&logoColor=white)

An intelligent, conversational AI chatbot built with Streamlit and Google Gemini. It crafts personalized travel itineraries and answers follow-up questions, all while staying strictly on topic.

## 🚀 About This Project

This application serves as a dedicated **AI Tour Planning Assistant**. Users can input their destination, trip duration, interests, and travel style to receive a detailed, day-by-day itinerary. The app's true power lies in its conversational ability: users can ask for modifications ("Can you add more museums to Day 2?"), request more details ("Tell me more about the restaurant on Day 3"), or ask for alternatives ("What's a different activity for the morning of Day 5?").

The chatbot is powered by the **Google Gemini** model and features a custom `system_instruction` that strictly confines its responses to travel planning, ensuring the AI remains focused and helpful for its intended purpose.

## 📸 Application Preview

*(**Recommendation:** Add a screenshot or a short GIF of your application in action here. A visual preview is the best way to showcase your project!)*

`[Image or GIF of the AI Tour Planner in action]`

## ✨ Key Features

* **Personalized Itineraries:** Generates bespoke travel plans based on user-defined destination, duration, interests, and travel style.
* **Conversational Follow-ups:** Uses session state to remember the generated itinerary, allowing users to have a stateful conversation and modify their plan.
* **Focused AI Personality:** A core feature! The app uses a strong `system_instruction` for the Gemini model, which **rejects all off-topic questions** (like math, history, or general knowledge) and politely redirects the user back to travel planning.
* **Streaming Responses:** AI responses are streamed in real-time for a more dynamic and engaging user experience.
* **Secure API Key Handling:** Safely loads the `GEMINI_API_KEY` using Streamlit Secrets for deployment or environment variables for local development.
* **Clean UI:** A simple, two-column layout using Streamlit's `st.sidebar` for inputs and `st.chat_message` for the conversation.
* **Conversation Reset:** A "Clear Conversation" button to easily start a new plan.

## 🧠 Core Logic: The System Instruction

A key design element of this chatbot is its "personality" and "guardrails," which are defined by the `SYSTEM_INSTRUCTION` passed to the Gemini model. This ensures the bot stays on task and doesn't become a general-purpose, off-topic chatbot.

The (abbreviated) instruction is:

> ```text
> You are an AI tour planning assistant.
> Your one and only job is to generate a travel itinerary... and then answer follow-up questions to modify... that specific itinerary.
> You MUST NOT answer any general knowledge questions...
> If the user asks an unrelated question, you MUST politely decline...
> ```

This makes the bot highly effective for its specific use case and is a great example of prompt engineering to control model behavior.

## ⚙️ How to Run This Project

### 1. Prerequisites

* [Python 3.7+](https://www.python.org/)
* A Google Gemini API Key. You can get one from the [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Clone the Repository

```bash
git clone [https://github.com/your-username/ai-tour-planner.git](https://github.com/your-username/ai-tour-planner.git)
cd ai-tour-planner