from typing import List, Dict, Any
from model import llm
from  datetime import datetime
from Supervisor import app
import streamlit as st
import librosa
import whisper
import json 
import io

@st.cache_resource
def load_whiper_model():
    return whisper.load_model('small',device='cuda')



def get_audio():
    try :
        model=load_whiper_model()
        recorded_audio=st.sidebar.audio_input(" ")
        if recorded_audio:
            
            audio_bytes = recorded_audio.read()
            audio_stream = io.BytesIO(audio_bytes)
            audio_array, _ = librosa.load(audio_stream, sr=16000)
            trans = model.transcribe(audio_array)
            return trans['text']
    except Exception as e:
        st.error(f"Audio error: {str(e)}")
        return None





if "history" not in st.session_state:
    st.session_state.history: List[Dict[str, Any]] = [] # type: ignore

# Display chat history
for msg in st.session_state.history:
    role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.write(msg["content"])
        if "agent" in msg:
            st.caption(f"Handled by: {msg['agent']}")




input_mode = st.sidebar.radio(
    "Select the mode of input",
    options=['Audio Input', 'Text Input'],  # Available choices
    index=0  # Default to first option
)

selection={'Audio Input':get_audio(),'Text Input':st.chat_input()}



if prompt:=selection[input_mode]:
# if prompt:    

    st.session_state.history.append({"role": "user", "content": prompt})

    # Display user message immediately
    with open("history.json", "a") as file:
        
        json_entry = json.dumps({
            "role": "user",
            "content": prompt,
            "timestamp": str(datetime.now())  # Optional: Add timestamp
        })
        file.write(json_entry + "\n")


            
    with st.chat_message("user"):
        st.write(prompt)

    # Process through LangGraph
    response_content = ""
    
    for step in app.stream(
        {"messages": [{"role": "user", "content": prompt}]},
        stream_mode="values",
    ):
        latest = step["messages"][-1]
        response_content = latest.content
        current_agent = latest.name if hasattr(latest, 'name') else "supervisor"

    # Append assistant response to session history
    st.session_state.history.append({
        "role": "assistant",
        "content": response_content,
        "agent": current_agent
    })

    # Append to JSON file (without overwriting)
    with open("chat_history.json", "a") as file:
        json_entry = json.dumps({
            "user_query": prompt,
            "assistant_response": response_content,
            "agent": current_agent,
            "timestamp": str(datetime.now())
        })
        file.write(json_entry + "\n")  # Newline separates entries

    # Display assistant response
    with st.chat_message("assistant"):
        st.write(response_content)
        st.caption(f"Handled by: {current_agent}")