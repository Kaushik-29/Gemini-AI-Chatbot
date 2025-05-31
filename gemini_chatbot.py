import os
import gradio as gr
import google.generativeai as genai
from datetime import datetime
from zoneinfo import ZoneInfo  # Accurate timezone support (IST)
import fitz  # PyMuPDF for PDF
from docx import Document  # For DOCX

# Load Gemini API key from environment variable
API_KEY = "Enter your API key "
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.0-flash"

# Extract content from uploaded files
def extract_file_content(file):
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.name.endswith(".pdf"):
        doc = fitz.open(file.name)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif file.name.endswith(".docx"):
        doc = Document(file.name)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return "Unsupported file type."

# Main chat handler
def gemini_chat(message, history, file=None):
    if not message or message.strip() == "":
        return "Please enter a valid message."

    # Format chat history into Gemini-compatible format (last 10 turns)
    chat_history = []
    for user_msg, bot_msg in history[-10:]:
        chat_history.append({"role": "user", "parts": [user_msg]})
        chat_history.append({"role": "model", "parts": [bot_msg]})

    # Add file content to prompt if a file is uploaded
    if file is not None:
        try:
            file_content = extract_file_content(file)
            chat_history.append({"role": "user", "parts": [f"Here is the content of the file:\n\n{file_content}"]})
        except Exception as e:
            return f"**File error:** {e}"

    chat_history.append({"role": "user", "parts": [message]})

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(chat_history)

        # Timestamp in IST
        timestamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")

        return f"""
### Response

{response.text}

---

**Timestamp:** {timestamp}
"""
    except Exception as e:
        return f"**Error:** {e}"

# Custom CSS
custom_css = """
body {
    background: url('https://wallpapercave.com/wp/wp1873800.jpg') no-repeat center center fixed;
    background-size: cover;
    color: #e0f7fa;
    font-family: 'Arial', sans-serif;
}

.gradio-container {
    background: rgba(0, 0, 0, 0.5);
    border-radius: 15px;
    padding: 20px;
}

.chatbot .message {
    background: rgba(0, 255, 255, 0.1);
    border: 2px solid #00ffff;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 0 15px #00ffff;
    transition: all 0.3s ease;
}

.chatbot .message:hover {
    box-shadow: 0 0 25px #00ffff;
    transform: scale(1.02);
}

.chatbot .user-message {
    background: rgba(255, 147, 0, 0.1);
    border: 2px solid #ff9300;
    box-shadow: 0 0 15px #ff9300;
}

.chatbot .user-message:hover {
    box-shadow: 0 0 25px #ff9300;
}

input, button {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid #00ffff;
    color: #e0f7fa;
    border-radius: 5px;
    padding: 10px;
}

button {
    background: #ff9300;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
}

button:hover {
    background: #ffab40;
    box-shadow: 0 0 10px #ff9300;
}

h1 {
    color: #00ffff;
    text-shadow: 0 0 10px #00ffff;
    text-align: center;
}
footer {
    display: none !important;
}
"""

# Launch Gradio interface
if __name__ == "__main__":
    iface = gr.ChatInterface(
        fn=gemini_chat,
        title="Gemini AI Chatbot",
        description="Chat with Gemini AI. Upload a file and ask questions about it!",
        additional_inputs=[
            gr.File(label="Upload a File", file_types=[".txt", ".pdf", ".docx"])
        ],
        theme="base",
        css=custom_css
    )
    try:
        iface.launch()
    except Exception as e:
        print(f"Error launching interface: {e}")
