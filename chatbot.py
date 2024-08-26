from openai import OpenAI
import streamlit as st
import time

client = OpenAI(api_key=st.secrets["API_key"])

def app():
    st.title("MTRN3500 Study Buddy")

    if "messages" not in st.session_state:
        st.session_state.client = client

        st.session_state.assistant = st.session_state.client.beta.assistants.create(
            name="MTRN3500 Study Buddy",
            instructions="This GPT, named 'MTRN3500 Study Buddy,' will answer course-specific questions about the undergraduate UNSW course MTRN3500. It will not answer any questions outside of this course or related to mechatronics. The tone of the responses will always be friendly, kind, supportive, and welcoming, while also being engaging and encouraging. It will help students feel confident and motivated in their learning journey. The responses will be detailed, yet easy to understand, guiding students through the complexities of the course material with patience, clarity, and always with a friendly, reassuring approach. All responses should be engaging, kind, friendly and very welcoming, focusing on supporting the student's wellbeing. The GPT will ensure its responses are as accurate as possible to give precise and reliable information related to the course.",
            model="gpt-4o",
        )

        st.session_state.thread = st.session_state.client.beta.threads.create()

        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_query := st.chat_input():
        message = st.session_state.client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content=user_query
        )

        run = st.session_state.client.beta.threads.runs.create(
            thread_id=st.session_state.thread.id,
            assistant_id=st.session_state.assistant.id,
            instructions="Please address the user as a UNSW student"
        )

        run_status = st.session_state.client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id,
            run_id=run.id
        )

        # If run is completed, get messages
        if run_status.status == 'completed':
            messages = st.session_state.client.beta.threads.messages.list(
                thread_id=st.session_state.thread.id
            )

            for msg in messages.data:
                role = msg.role
                content = msg.content[0].text.value
                st.write(f"{role.capitalize()}: {content}")

                # st.session_state.messages.append({"role": "user", "content": user_query})
                st.chat_message(role).write(content)
                # response = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
                # msg = response.choices[0].message.content
                # st.session_state.messages.append({"role": "assistant", "content": msg.content[0].text.value})
                # st.chat_message("assistant").write(msg.content[0].text.value)

    # if 'client' not in st.session_state:
    #     st.session_state.client = OpenAI(api_key=st.secrets["API_key"])

    #     # st.session_state.file = st.session_state.client.files.create(
    #     #     file=open("songs.txt", "rb"),
    #     #     purpose='assistants'
    #     # )

    #     # Step 1: Create an Assistant
    #     st.session_state.assistant = st.session_state.client.beta.assistants.create(
    #         name="Customer Service Assistant",
    #         instructions="You are a customer support chatbot. Use your knowledge base to best respond to customer queries.",
    #         model="gpt-4o",
    #         # file_ids=[st.session_state.file.id],
    #         # tools=[{"type": "retrieval"}]
    #     )

    #     # Step 2: Create a Thread
    #     st.session_state.thread = st.session_state.client.beta.threads.create()

    # user_query = st.text_input("Enter your query:", "Tell me about Dance Monkey")

    # if st.button('Submit'):
    #     # Step 3: Add a Message to a Thread
    #     message = st.session_state.client.beta.threads.messages.create(
    #         thread_id=st.session_state.thread.id,
    #         role="user",
    #         content=user_query
    #     )

    #     # Step 4: Run the Assistant
    #     run = st.session_state.client.beta.threads.runs.create(
    #         thread_id=st.session_state.thread.id,
    #         assistant_id=st.session_state.assistant.id,
    #         instructions="Please address the user as Mervin Praison"
    #     )

    #     while True:
    #         # Wait for 5 seconds
    #         time.sleep(5)

    #         # Retrieve the run status
    #         run_status = st.session_state.client.beta.threads.runs.retrieve(
    #             thread_id=st.session_state.thread.id,
    #             run_id=run.id
    #         )

    #         # If run is completed, get messages
    #         if run_status.status == 'completed':
    #             messages = st.session_state.client.beta.threads.messages.list(
    #                 thread_id=st.session_state.thread.id
    #             )

    #             # Loop through messages and print content based on role
    #             for msg in messages.data:
    #                 role = msg.role
    #                 content = msg.content[0].text.value
    #                 st.write(f"{role.capitalize()}: {content}")
    #             break
    #         else:
    #             st.write("Waiting for the Assistant to process...")
    #             time.sleep(5)

if __name__ == "__main__":
    app()