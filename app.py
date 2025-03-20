import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from google.api_core.exceptions import ResourceExhausted
import tenacity
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API Key
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Google Gemini Model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", temperature=0.9)

# Define Prompt Template
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Tell me a joke about {topic}. Make it funny and engaging!"
)

# Create LangChain Model
chain = LLMChain(llm=llm, prompt=prompt)

# Streamlit UI Setup
st.title("🤣 AI Joke Generator")
st.write("Ask for a joke on any topic!")

# Chat Input
user_input = st.text_input("Enter a joke request...")

# Function to Fetch Joke with Retry Mechanism
@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=2, min=5, max=20),
    retry=tenacity.retry_if_exception_type(ResourceExhausted),
)
def get_joke(topic):
    return chain.invoke({"topic": topic})

if user_input:
    try:
        response = get_joke(user_input)["text"]
    except ResourceExhausted:
        response = "⚠️ API limit reached! Try again later."

    st.write(f"**Joke:** {response}")
