from openai import OpenAI
import streamlit as st
import time

client = OpenAI(api_key=st.secrets["API_key"])

def app():
    st.title("MTRN3500 Study Buddy")

    if "messages" not in st.session_state:
        st.session_state.client = client

        # create an Assistant
        st.session_state.assistant = st.session_state.client.beta.assistants.create(
            name="MTRN3500 Study Buddy",
            instructions="This GPT, named 'MTRN3500 Study Buddy,' will answer course-specific questions about the undergraduate UNSW course MTRN3500. It will not answer any questions outside of this course or related to mechatronics. The tone of the responses will always be friendly, kind, supportive, and welcoming, while also being engaging and encouraging. It will help students feel confident and motivated in their learning journey. The responses will be detailed, yet easy to understand, guiding students through the complexities of the course material with patience, clarity, and always with a friendly, reassuring approach. All responses should be engaging, kind, friendly and very welcoming, focusing on supporting the student's wellbeing. The GPT will ensure its responses are as accurate as possible to give precise and reliable information related to the course.",
            model="gpt-4o",
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
        # response = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
        msg = messages.data[0].content[0].text.value
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

if __name__ == "__main__":
    app()