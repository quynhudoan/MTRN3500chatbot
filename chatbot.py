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
from google.oauth2 import service_account
from googleapiclient.discovery import build

client = OpenAI(api_key=st.secrets["API_key"])
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Function to authenticate and get Google Drive service
def authenticate_gdrive():
    creds = None

    service_account_info = {
        "type": st.secrets["gcp_service_account"]["type"],
        "project_id": st.secrets["gcp_service_account"]["project_id"],
        "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
        "private_key": st.secrets["gcp_service_account"]["private_key"],
        "client_email": st.secrets["gcp_service_account"]["client_email"],
        "client_id": st.secrets["gcp_service_account"]["client_id"],
        "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
        "token_uri": st.secrets["gcp_service_account"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"],
        "universe_domain": st.secrets["gcp_service_account"]["universe_domain"]
    }

    # if 'token' not in st.session_state:
    creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    st.session_state['token'] = creds
    # else:
        # creds = Credentials.from_authorized_user_info(st.session_state['token'])

    # create a Google Drive service
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_file_to_gdrive(service, file_name):
    file_metadata = {
        'name': file_name,
        'mimeType': 'application/json'
    }
    
    # Upload the file
    media = MediaFileUpload(file_name, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    st.success(f"File uploaded successfully with file ID: {file.get('id')}")
    return file.get('id')

def share_file_with_user(service, file_id):
    permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': 'quynhd2001@gmail.com'
    }
    
    service.permissions().create(
        fileId=file_id,
        body=permission,
        fields='id'
    ).execute()

    st.write(f"File ID {file_id} is shared with quynhd2001@gmail.com.")

def app():
    img = Image.open("logo.png")
    new_size = (150, 60)
    img = img.resize(new_size)
    st.image(img)

    st.title("MTRN3500 Study Buddy")
    st.write("This Chatbot is in the development stage and can therefore make mistakes! Please check all important information with tutors to ensure accuracy.")

    authenticate_gdrive()

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

        json_data = json.dumps(api_data, indent=4, default = str)
        file_name = 'api_logs.json'

        with open(file_name, 'w') as json_file:
            json_file.write(json_data)

        if 'token' in st.session_state:
            service = authenticate_gdrive()
            file_id = upload_file_to_gdrive(service, file_name)

            file_url = f"https://drive.google.com/file/d/{file_id}/view"
            st.write(f"View the file in Google Drive: [View File]({file_url})")

            share_file_with_user(service, file_id)


if __name__ == "__main__":
    app()