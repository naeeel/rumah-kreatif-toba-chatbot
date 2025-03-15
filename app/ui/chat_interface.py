import streamlit as st
import requests
import json
from datetime import datetime

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"

def display_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        with st.chat_message(role):
            st.write(content)

def add_message(role, content):
    """Add a message to the chat history"""
    st.session_state.messages.append({"role": role, "content": content})

def send_message_to_api(message):
    """Send message to chatbot API and get response"""
    api_url = "http://localhost:8000/chat"  # Update with your API URL
    
    payload = {
        "message": message,
        "user_id": st.session_state.user_id
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with API: {str(e)}")
        return "Maaf, terjadi kesalahan saat berkomunikasi dengan server."

def main():
    st.title("💬 Rumah Kreatif Toba Chatbot")
    
    # Initialize session state
    init_session_state()
    
    # Display header
    st.markdown("""
    Selamat datang di layanan chatbot Rumah Kreatif Toba. Chatbot ini dapat:
    - Menjawab pertanyaan tentang produk dan layanan kami
    - Mengecek stok produk secara real-time
    - Melacak status pesanan Anda
    - Memberikan rekomendasi produk
    
    Silakan ajukan pertanyaan untuk memulai.
    """)
    
    # Display chat messages
    display_messages()
    
    # Get user input
    if prompt := st.chat_input("Tulis pesan Anda di sini..."):
        # Add user message to chat
        add_message("user", prompt)
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get chatbot response (with spinner)
        with st.spinner("Chatbot sedang mengetik..."):
            response = send_message_to_api(prompt)
        
        # Add and display chatbot response
        add_message("assistant", response)
        with st.chat_message("assistant"):
            st.write(response)

if __name__ == "__main__":
    main()