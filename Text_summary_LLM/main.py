import requests
from bs4 import BeautifulSoup
import ollama
import streamlit as st

# Model Ollama
MODEL = "llama3.2"

# Website class to fetch and parse website content
class Website:
    url: str
    title: str
    text: str

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup(["script", "style","img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

# desigin system prompt
system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related \
Respond in markdown."

# design user prompt
def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "The contents of this website is an follows; \
        please provide a short summary of this website in markdown format. \
        If it includes news or announcements, them summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

# design message for Ollama
def messege_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

# Ollama call
def summarize(url):
    try:
        website = Website(url)
        messages = messege_for(website)
        response = ollama.chat(MODEL, messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"Error summarizing the website: {e}"
    
# Streamlit app to display the summary

st.title("Website Summary Generator")
st.markdown(
    "Enter a URL to get a summary of the website."
)

url = st.text_input("Enter URL:", "")

if st.button("Summarize"):
    if url:
        with st.spinner("Summarizing..."):
            summary = summarize(url)
        st.markdown(summary)

    else:
        st.warning("Please enter a valid URL.")