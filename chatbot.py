from openai import OpenAI
import streamlit as st

# openai.api_key = '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'
client = OpenAI(api_key='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')

# def get_reply(input_string):
#     response = client.chat.completion.create(
#         model = "gpt-4o",
#         prompt="Hello, how can I help you?",
#         max_tokens=50
#     )

def app():
    st.title("MTRN3500 Study Buddy")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

if __name__ == "__main__":
    app()