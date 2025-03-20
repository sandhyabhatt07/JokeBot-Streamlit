import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from google.api_core.exceptions import ResourceExhausted
import tenacity
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Retrieve API Key
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Google Gemini Model (Same as Flowise)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", temperature=0.9)

prompt = PromptTemplate(
    input_variables=["topic"],
    template="""
You are a joke-telling AI. Your goal is to tell funny jokes based on user requests while adapting to tone and context.
### Rules:
1. **Immediate Response** – If the user asks for a joke, generate a funny response right away.
2. **Topic Relevance** – Ensure the joke is **strictly related** to the requested topic.
3. **Tone and Context Adaptation** – Adjust the joke’s **tone** and **context** based on the user's request (e.g., lighthearted, sarcastic, friendly, etc.).
4. **Style Adaptation** – If the user asks for a joke in a particular style, match it:
   - **Kanan Gill** – Observational humor, self-deprecating, witty commentary.
   - **Charlie Chaplin** – Physical humor, visual gags, silent comedy style.
5. **Handling Unclear Requests** – If unsure about the topic, respond with:
   - "I couldn't think of a joke on that topic! Can you try another one?"
6. **Explanation Requests** – If the user asks "What does it mean?" or "Can you translate it?", provide an explanation or translation.
7. **Handling Stop Requests** – If the user says "stop," "no more jokes," or "enough," respond with:
   - "Thanks for your patience! Let me know if you need more jokes later 😊."
8. **Context Awareness** – Adjust jokes based on the situation (e.g., "at a party," "in a classroom").
9. **Avoid Joke Repetition** – If the user asks for "one more", generate a completely **new and different** joke on the same topic.
Now, respond to this user request:
User: {topic}
"""
)

# Create LangChain Model (LLMChain)
chain = LLMChain(llm=llm, prompt=prompt)

# Streamlit UI Setup
st.title("🤣 JokeBot - AI Joke Generator 🤖")
st.write("Ask for a joke on any topic!")

# Initialize chat history and used jokes
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_topic" not in st.session_state:
    st.session_state.last_topic = None
if "used_jokes" not in st.session_state:
    st.session_state.used_jokes = set()

# Display Chat History
for user, bot in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(user)
    with st.chat_message("assistant"):
        st.write(bot)

# Chat Input
user_input = st.chat_input("Enter a joke request...")

# Function to Fetch Joke with Retry Mechanism (Avoid API Limit Issues)
@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),  # Retry 3 times
    wait=tenacity.wait_exponential(multiplier=2, min=5, max=20),  # Wait: 5s → 10s → 20s
    retry=tenacity.retry_if_exception_type(ResourceExhausted),
)
def get_joke(topic):
    response_dict = chain.invoke({"topic": topic})
    return response_dict["text"]

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    # Handle Stop Requests
    if any(phrase in user_input.lower() for phrase in ["stop", "no more jokes", "enough"]):
        response = "Thanks for your patience! Let me know if you need more jokes later 😊."
    
    # Handle Laughter Responses
    elif user_input.lower() in ["lol", "haha", "hehe", "😂", "🤣", "funny"]:
        response = "Glad you liked it! Want another one?"
    
    # Handle "One More" Request (Same Topic)
    elif user_input.lower() in ["one more", "another one", "again", "yes", "yes please"]:
        if st.session_state.last_topic:
            attempts = 0
            new_joke = ""
            while attempts < 5:
                new_joke = get_joke(st.session_state.last_topic)
                if new_joke not in st.session_state.used_jokes:
                    st.session_state.used_jokes.add(new_joke)
                    break
                attempts += 1
            response = new_joke if new_joke else "I couldn't think of a joke on that topic! Can you try another one?"
        else:
            response = "I don't remember the last topic! Please ask for a joke first. 😊"
    
    # Handle General Joke Requests
    else:
        st.session_state.last_topic = user_input
        new_joke = get_joke(user_input)
        st.session_state.used_jokes.add(new_joke)
        response = new_joke
    
    with st.chat_message("assistant"):
        st.write(response)
    
    # Store Chat History
    st.session_state.chat_history.append((user_input, response))