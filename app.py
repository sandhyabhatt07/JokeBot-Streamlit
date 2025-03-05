#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import requests

# Set the API URL (Change this to your Flowise API)
API_URL = "http://localhost:3000/canvas/4af4e932-2018-459e-9597-cd6ec09c5652"  

st.set_page_config(page_title="JokeBot 🤖", layout="centered")

st.title("🤣 JokeBot - AI Joke Generator(MemoryLess Chatbot 🤖")
st.write("Ask me for a joke about any topic, and I'll make you laugh!")

# User input
user_input = st.text_input("Enter a joke topic:", "")

if user_input:
    # Send request to Flowise API
    response = requests.post(API_URL, json={"question": user_input})

    if response.status_code == 200:
        joke = response.json().get("text", "Oops! Couldn't fetch a joke.")
        st.success(joke)
    else:
        st.error("Error fetching joke. Please try again.")

st.markdown("Created with ❤️ using Flowise & Streamlit")

