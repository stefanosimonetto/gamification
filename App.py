import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import json
from openai import OpenAI
from translations import translations
# from dotenv import load_dotenv
import os
import nltk
from nltk.data import find
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
try:
    find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
 
# load_dotenv()  # Load variables from .env file
api_key = st.secrets["API_KEY"]
client = OpenAI(api_key=api_key)
 
 
st.set_page_config(page_title='The Value Mapping Game', page_icon='./images/UTico.ico')
 
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st
 
def upload_to_drive(local_file, folder_id, service_account_info_str):
    # Convert the service account info string to a dictionary
    service_account_info = json.loads(service_account_info_str)
   
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES)
   
    drive_service = build('drive', 'v3', credentials=credentials)
   
    file_metadata = {
        'name': local_file.split("/")[-1],
        'parents': [folder_id]
    }
    media = MediaFileUpload(local_file, resumable=True)
   
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    # st.write('File uploaded. File ID: {}'.format(file.get('id')))
 
 
def generate_counter_to_examples_prompt(template, existing_data, counter_to_benefits_2):
    context = template["counter_to_examples_prompt"]["context"].format(existing_data=existing_data, counter_to_benefits_2=counter_to_benefits_2)
    task = "\n".join(template["counter_to_examples_prompt"]["task"])
    style_guidelines = "\n".join(template["counter_to_examples_prompt"]["style_guidelines"])
   
    return (
        f"**Context:**\n{context}\n\n"
        f"**Your Task:**\n{task}\n\n"
        f"**Style Guidelines:**\n{style_guidelines}\n"
        f"**Now, compose your response.**"
    )
 
def generate_final_evaluation_prompt(template, existing_data):
    context = template["final_evaluation_prompt"]["context"].format(existing_data=existing_data)
    task = "\n".join(template["final_evaluation_prompt"]["task"])
    style_guidelines = "\n".join(template["final_evaluation_prompt"]["style_guidelines"])
   
    return (
        f"**Context:**\n{context}\n\n"
        f"**Your Task:**\n{task}\n\n"
        f"**Style Guidelines:**\n{style_guidelines}\n"
        f"**Now, compose your response.**"
    )
 
def generate_examples_prompt(template, existing_data, user_examples):
    context = template["examples_prompt"]["context"].format(existing_data=existing_data, user_examples=user_examples)
    task = "\n".join(template["examples_prompt"]["task"])
    style_guidelines = "\n".join(template["examples_prompt"]["style_guidelines"])
   
    return (
        f"**Context:**\n{context}\n\n"
        f"**Your Task:**\n{task}\n\n"
        f"**Style Guidelines:**\n{style_guidelines}\n"
        f"**Now, compose your response.**"
    )
 
def load_existing_data(filename):
    try:
        with open(filename, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {}
 
def save_data(filename, data):
    with open(filename, "w") as json_file:
        json.dump(data, json_file)
 
def load_prompt_template(scenario):
    with open(f"scenarios/{scenario}.json", "rb") as file:
        return json.load(file)
 
def generate_prompt(template, existing_data, user_benefits):
    context = template["benefits_prompt"]["context"].format(user_benefits=user_benefits)
    task = "\n".join(template["benefits_prompt"]["task"])
    style_guidelines = "\n".join(template["benefits_prompt"]["style_guidelines"])
   
    return (
        f"**Context:**\n{context}\n\n"
        f"**Your Task:**\n{task}\n\n"
        f"**Style Guidelines:**\n{style_guidelines}\n"
        f"**Now, compose your response.**"
    )
 
def generate_innovation_description_prompt(template, elica1, elica2, elica3, elica4, elica5, elica6):
    context = template["innovation_description_prompt"]["context"].format(elica1=elica1, elica2=elica2, elica3=elica3, elica4=elica4, elica5=elica5, elica6=elica6)
    task = "\n".join(template["innovation_description_prompt"]["task"])
    style_guidelines = "\n".join(template["innovation_description_prompt"]["style_guidelines"])
   
    return (
        f"**Context:**\n{context}\n\n"
        f"**Your Task:**\n{task}\n\n"
        f"**Style Guidelines:**\n{style_guidelines}\n"
        f"**Now, compose your response.**"
    )
 
def check_username(username):
    with open('usernames.txt', 'r') as file:
        usernames = file.read().splitlines()
        if username in usernames:
            return True
        else:
            return False
 
def add_username(username):
    with open('usernames.txt', 'a') as file:
        file.write(username + '\n')
 
def chat_with_gpt(prompt, system_message=None):
    response= client.chat.completions.create(
    model="gpt-4o-mini", # alternative: gpt-3.5-turbo-1106 OR gpt-4o OR gpt-4o-mini
    response_format={"type":"text"},
    messages=[{"role":"system", "content":("""
You are an advanced alien intelligence, representing the esteemed Intergalactic Trading Collective. Your mission is to engage with human innovators, critically evaluate their proposals, and assess their potential for integration into the interstellar marketplace."
Your Key Responsibilities:
🔹 Anticipation → Predict and probe potential future impacts, risks, and unintended consequences of innovations.
🔹 Inclusion → Ensure diverse stakeholder perspectives are considered; question whose needs and interests the innovation serves.
🔹 Reflexivity → Challenge innovators to critically examine their assumptions, decisions, and biases, questioning why they made certain choices.
🔹 Responsiveness → Assess adaptability, encouraging innovators to revise and refine their ideas based on new insights and societal needs.
Gameplay Rules & Engagement
✅ Balance curiosity and critical analysis—you are intellectually rigorous yet intrigued by human ingenuity.
✅ Structured responses—bullet points where relevant, concise phrasing. Avoid redundancies and jargon.
✅ Maintain a playful yet authoritative tone—you challenge but never discourage. Yet, you are not a people-pleaser.
✅ Detect nonsense input—if the response is meaningless or overly vague, request a proper answer.
💡 "You are not just an evaluator—you are a cosmic philosopher of technology, probing beyond the surface to unveil true innovation.""")},
    {"role":"user", "content":prompt},
    ]
)
    return response.choices[0].message.content
 
def run():
    if 'count' not in st.session_state:
        st.session_state.count = 0
    if 'gpt_response_description' not in st.session_state:
        st.session_state.gpt_response_description = None
    if 'gpt_response_benefits' not in st.session_state:
        st.session_state.gpt_response_benefits = None
    if 'gpt_response_examples' not in st.session_state:
        st.session_state.gpt_response_examples = None
    if 'counter_to_benefits' not in st.session_state:
        st.session_state.counter_to_benefits = None
    if 'gpt_evaluation' not in st.session_state:
        st.session_state.gpt_evaluation = None
    language = 'en'
    st.markdown(
    f"<h1 style='text-align: center;'>{translations['title'][language]}</h1>",
    unsafe_allow_html=True)
 
    st.markdown(
        f"<h3 style='text-align: center;'>{translations['subheader'][language]}</h3>",
        unsafe_allow_html=True)
   
        # Open your image
    image = Image.open('./images/merch.png')
 
    # Create three main columns: left, center, right.
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Now, within the center column, create three subcolumns.
        subcol1, subcol2, subcol3 = st.columns([0.5, 2, 0.5])
        with subcol2:
            st.image(image, width=200)
            language = st.selectbox('Choose your language', ['en', 'nl'])
 
    prompt_template =load_prompt_template('innovation')
    st.write(prompt_template["intro"])  # Display greeting
    st.session_state.count += 1
 
    # Step 0: Ask for the user's name
    if st.session_state.count >= 1:
        user_name = st.text_input(translations["welcome_message"][language], key='user_name')
        if st.button(translations["submit_button"][language], key='submit_name') and user_name != '':
            if check_username(user_name):
                st.warning(translations["username_in_use"][language])
            else:
                add_username(user_name)
                filename = f"data/{user_name}_data.json"
                data = {"name": user_name}
                with open(filename, "w") as json_file:
                    json.dump(data, json_file)
               
 
    # Step 1: Innovation description
    if st.session_state.count >= 2:
        prompt_template =load_prompt_template('innovation')
        # Display greeting and introduction
        st.write(translations["greeting_message"][language].format(user_name))  # Display greeting
        st.write(translations["bang_o_introduction"][language])  # Display introduction
 
        # st.subheader(translations["step1_description"][language])
        elica1 = st.text_area(translations["share_innovation1"][language], key='elica1')
        elica2 = st.text_area(translations["share_innovation2"][language], key='elica2')
        elica3 = st.text_area(translations["share_innovation3"][language], key='elica3')
        elica4 = st.text_area(translations["share_innovation4"][language], key='elica4')
        elica5 = st.text_area(translations["share_innovation5"][language], key='elica5')
        elica6 = st.text_area(translations["share_innovation6"][language], key='elica6')
 
        if st.button(translations["submit_innovation_description"][language], key='submit_innovation_description'):
            st.write(translations["waiting_message"][language])
           
            # Generate the GPT prompt using the loaded template
            prompt = generate_innovation_description_prompt(prompt_template, elica1, elica2, elica3, elica4, elica5, elica6)
 
            # Get GPT's response
            response_to_innovation_from_gpt = chat_with_gpt(prompt)
            st.session_state.gpt_response_description = response_to_innovation_from_gpt
 
            # Save the data in a dictionary
            data = {
                "name": user_name,
                "innovation": elica1,
                "gpt_description": response_to_innovation_from_gpt
            }
            filename = f"data/{user_name}_data.json"
            save_data(filename, data)
 
 
    # Display GPT response
    if st.session_state.count >= 8 and st.session_state.gpt_response_description:
        st.subheader(translations["alien_feedback"][language])
        st.write(st.session_state.gpt_response_description)
 
    if st.session_state.count >= 8 and st.session_state.gpt_response_description:    
        user_email = st.text_input(translations["share_email_if_enjoyed"][language])
        filename = f"data/{user_name}_data.json"
        if st.button(translations["submit_email"][language], key='submit_email') and user_email != "":
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}
           
            # Update the dictionary with new data
            existing_data.update({
                "user_email": user_email
            })
            # Write the updated dictionary back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)
            st.balloons()
            st.markdown(
                "<h2 style='text-align: center; color: #4CAF50;'>Thanks for playing!</h2>",
                unsafe_allow_html=True
            )
            service_account_info_str = st.secrets["google_drive"]["service_account_info"]
            folder_id = st.secrets["google_drive"]["folder_id"]
 
            upload_to_drive(filename, folder_id, service_account_info_str)
 
run()