from openai import OpenAI
import streamlit as st
from streamlit-js-eval import streamlit_js_eval

st.set_page_config(page_title="OpenAI API Example", page_icon=':material/chat:')
st.title("ChatBOT with OpenAI API")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_messages_count" not in st.session_state:
    st.session_state.user_messages_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_completed" not in st.session_state:
    st.session_state.chat_completed = False



def complete_setup():
    st.session_state.setup_complete = True
def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete:

    if "name" not in st.session_state:
        st.session_state.name = ""
    if "experience" not in st.session_state:
        st.session_state.experience = ""
    if "skills" not in st.session_state:
        st.session_state.skills = ""

    st.subheader("Personal Information", divider="rainbow")

    st.session_state.name = st.text_input("Name", max_chars=40, value=st.session_state.name, placeholder="Enter your name")

    st.session_state.experience = st.text_area("Experience", value=st.session_state.experience, height=None, max_chars=200, placeholder="Describe your experience")

    st.session_state.skills = st.text_area("Skills", value=st.session_state.skills, height=None,max_chars=200, placeholder="List your skills")

    st.subheader("Company and Position", divider="rainbow")

    if "level" not in st.session_state:
        st.session_state.level = "Junior"
    if "position" not in st.session_state:
        st.session_state.position = "Data Scientist"  
    if "company" not in st.session_state:
        st.session_state.company = "Amazon"
    
    col1, clo2 = st.columns(2)

    with col1:
        st.session_state.level = st.radio("Choose level", 
                        options=["Junior", "Mid-level", "Senior"], 
                        key="vivisbility", 
                        index=None, 
                        help="Select level"
                        )

    with clo2:
        st.session_state.position = st.selectbox("Choose a position", 
                                options=["Data Scientist", "Data Engineer", "Machine Learning Engineer", "BI Analyst", "Financial Analyst"], 
                                help="Choose a position"
                                )

    st.session_state.company = st.selectbox("Choose a Company", 
                        options=["Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify"], 
                        help="Select a company"
                        )

    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete! You can now start the interview.")

if st.session_state.setup_complete and not st.session_state.chat_completed and not st.session_state.feedback_shown:
    st.subheader("Interview Chat", divider="rainbow")
    st.info(
        "You are now in the interview chat. Start by introducing yourself.",
        icon=":material/waving_hand:"
        )
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-5.4-mini"

    if not st.session_state.messages:
        st.session_state.messages = [{
            "role":"system", 
            "content": f"You are an HR executive that interviews an interviewee called {st.session_state.name} with expirience {st.session_state.experience} and skills {st.session_state.skills}. You should interview him for the position {st.session_state.level} {st.session_state.position} at the company {st.session_state.company}"
            }]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    if st.session_state.user_messages_count < 5:
        if prompt := st.chat_input("Ask me anything!", max_chars=200, placeholder="Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_messages_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                    model=st.session_state.openai_model,
                    messages = [
                        {"role": m["role"], "content": m["content"]} 
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
                response = st.write_stream(stream)

                st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.user_messages_count += 1
    if st.session_state.user_messages_count >= 5:
        st.session_state.chat_completed = True
        st.success("You have completed the interview chat", icon=":material/check_circle:")
if st.session_state.chat_completed and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Providing feedback based on your interview performance...")
if st.session_state.feedback_shown:
    st.subheader("Feedback", divider="rainbow")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages if msg["role"] != "system"])

    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    feedback_completion = feedback_client.chat.completions.create(
        model=st.session_state.openai_model,
        messages=[
            {"role": "system", "content": """You are a helpful tool that provides feedback on an interviewee performance.
             Before the Feedback give a score of 1 to 10.
             Follow this format:
             Overal Score: //Your score
             Feedback: //Here you put your feedback
             Give only the feedback do not ask any additional questins.
              """},
            {"role": "user", "content": f"This is the interview you need to evaluate. Keep in mind that you are only a tool. And you shouldn't engage in any converstation: {conversation_history}"}
        ]
    )

    st.write("Feedback:")
    st.write(feedback_completion.choices[0].message["content"])
    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval.run_js(js_expression="parent.window.location.reload()")