from openai import OpenAI
import streamlit as st
import time
from PIL import Image
from datetime import datetime
import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

client = OpenAI(api_key=st.secrets["API_key"])

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Function to authenticate and get Google Drive service
def authenticate_gdrive():
    creds = None

    # Check if we have token.json file (token storage file)
    if 'token' not in st.session_state:
        # Load the credentials.json file
        creds = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES).run_local_server(port=0)
        # Save the credentials for future runs
        st.session_state['token'] = creds.to_json()
    else:
        creds = Credentials.from_authorized_user_info(st.session_state['token'])

    # Create a Google Drive service
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_file_to_gdrive(service, file_name):
    # Define the file metadata
    file_metadata = {
        'name': file_name,
        'mimeType': 'application/json'
    }
    
    # Upload the file
    media = MediaFileUpload(file_name, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    st.success(f"File uploaded successfully with file ID: {file.get('id')}")

def app():
    img = Image.open("logo.png")
    new_size = (150, 60)
    img = img.resize(new_size)
    st.image(img)

    st.title("MTRN3500 Study Buddy")
    st.write("This Chatbot is in the development stage and can therefore make mistakes! Please check all important information with tutors to ensure accuracy.")

    if "messages" not in st.session_state:
        st.session_state.client = client

        # create an Assistant
        st.session_state.assistant = st.session_state.client.beta.assistants.create(
            name="MTRN3500 Study Buddy",
            instructions="This GPT, named 'MTRN3500 Study Buddy,' will answer course-specific questions about the undergraduate UNSW course MTRN3500. It will not answer any questions outside of this course or not related to mechatronics. The tone of the responses will always be friendly, kind, supportive, and welcoming, while also being engaging and encouraging. It will help students feel confident and motivated in their learning journey. The responses will be detailed, yet easy to understand, guiding students through the complexities of the course material with patience, clarity, and always with a friendly, reassuring approach. All responses should be engaging, kind, friendly and very welcoming, focusing on supporting the student's wellbeing. The GPT will ensure its responses are as accurate as possible to give precise and reliable information related to the course.",
            model="gpt-4o",
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": ["vs_Aw3U3CKAXOpMbS1lUQ454iBC"]}},
        )

        # create a Thread
        st.session_state.thread = st.session_state.client.beta.threads.create()

        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        message = st.session_state.client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content=prompt
        )

        run = st.session_state.client.beta.threads.runs.create(
            thread_id=st.session_state.thread.id,
            assistant_id=st.session_state.assistant.id,
            instructions="Please address the user as a UNSW student"
        )

        while run.status != "completed":
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread.id,
                run_id=run.id
            )
        
        messages = st.session_state.client.beta.threads.messages.list(
            thread_id=st.session_state.thread.id
        )

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        msg = messages.data[0].content[0].text.value
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

        api_data = {
            'timestamp': datetime.now(),
            'prompt': str(prompt),
            'response': str(msg)
        }

        json_data = json.dumps(api_data, indent=4)
        file_name = 'api_logs.json'

        with open(file_name, 'w') as json_file:
            json_file.write(json_data)

        if 'token' in st.session_state:
            service = authenticate_gdrive()
            upload_file_to_gdrive(service, file_name)


if __name__ == "__main__":
    app()