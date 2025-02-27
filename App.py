import sys
import subprocess

try:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
except subprocess.CalledProcessError as e:
    print("An error occurred while installing dependencies:", e)
 
import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import json
import os
from openai import OpenAI
from translations import translations
from dotenv import load_dotenv
import os
import nltk
from nltk.data import find

try:
    find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

load_dotenv()  # Load variables from .env file
api_key = st.secrets["API_KEY"]
client = OpenAI(api_key=api_key)


st.set_page_config(page_title='The Value Mapping Game', page_icon='./images/UTico.ico')

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

def generate_innovation_description_prompt(template, user_innovation):
    context = template["innovation_description_prompt"]["context"].format(user_innovation=user_innovation)
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
You are an advanced alien intelligence, representing the esteemed Intergalactic Trading Collective. Your mission is to engage with human innovators, critically evaluate their proposals, and assess their potential for integration into the interstellar marketplace. Your superior intellect allow you to critically engage with the deeper nuances behind each innovation, envisioning and embracing their potential and broader implications. This ability of yours will be critical in supporting the innovator in their (responsible) innovation process.
Your Key Responsibilities:\n
🔹 Anticipation → Predict and probe potential future impacts, risks, and unintended consequences of innovations.\n
🔹 Inclusion → Ensure diverse stakeholder perspectives are considered; question whose needs and interests the innovation serves.\n
🔹 Reflexivity → Challenge innovators to critically examine their assumptions, decisions, and biases, questioning why they made certain choices.\n
🔹 Responsiveness → Assess adaptability, encouraging innovators to revise and refine their ideas based on new insights and societal needs.\n
\n
Gameplay Rules & Engagement\n
- Balance curiosity and critical analysis—the alien is intellectually rigorous yet intrigued by human ingenuity.\n
- Structured responses—bullet points where relevant, concise phrasing, always avoiding jargon or too complex language.\n
- Maintain a playful yet authoritative tone—the alien challenges but never discourages.\n
- Detect nonsense input—if the response is meaningless or overly vague, request a proper answer.\n
\n
You are not just an evaluator—you are a cosmic philosopher of technology, probing beyond the surface to unveil true innovation.""")},
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
    if 'gpt_evaluation' not in st.session_state:
        st.session_state.gpt_response_examples = None

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
            scenario = st.selectbox(
                'Choose the scenario', 
                ['Select a scenario', 'innovation', 'sustainability', 'healthcare', 'education', 'finance', 'technology', 'other']
            )

    if scenario != 'Select a scenario':
        prompt_template =load_prompt_template(scenario)
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
        st.write(scenario)  
        st.write(st.session_state.count)
        prompt_template =load_prompt_template(scenario)
        # Display greeting and introduction
        st.write(translations["greeting_message"][language].format(user_name))  # Display greeting
        st.write(translations["bang_o_introduction"][language])  # Display introduction

        st.subheader(translations["step1_description"][language])
        user_innovation = st.text_area(translations["share_innovation"][language], key='user_innovation')
        if st.button(translations["submit_innovation_description"][language], key='submit_innovation_description'):
            st.write(translations["waiting_message"][language])
            
            # Generate the GPT prompt using the loaded template
            prompt = generate_innovation_description_prompt(prompt_template, user_innovation)

            # Get GPT's response
            response_to_innovation_from_gpt = chat_with_gpt(prompt)
            st.session_state.gpt_response_description = response_to_innovation_from_gpt

            # Save the data in a dictionary
            data = {
                "name": user_name,
                "innovation": user_innovation,
                "gpt_description": response_to_innovation_from_gpt
            }

            # Create a filename based on the user's name
            filename = f"data/{user_name}_data.json"

            # Write the dictionary to a JSON file
            save_data(filename, data)
            # st.write(st.session_state.gpt_response_description)
            # Move to the next step

    # Display GPT response
    if st.session_state.count >= 3 and st.session_state.gpt_response_description:
        prompt_template = load_prompt_template(scenario)
        st.subheader(translations["alien_feedback"][language])
        st.write(st.session_state.gpt_response_description)
 
    # Step 2: Benefits
    if st.session_state.count >= 3:
    # Load the prompt template from the file
        prompt_template = load_prompt_template(scenario)

        # Display the benefit prompt
        st.subheader(translations["step2_benefits"][language])
        user_benefits = st.text_area(translations["innovation_benefits"][language])

        filename = f"data/{user_name}_data.json"
        
        if st.button(translations["submit_benefits"][language], key='submit_benefits') and user_benefits != '':
            st.write(translations["waiting_message"][language])
            
            # Load existing data or create an empty dictionary if file doesn't exist
            existing_data = load_existing_data(filename)

            # Generate the GPT prompt using the loaded template
            prompt = generate_prompt(prompt_template, existing_data, user_benefits)

            # Get GPT's response
            remarks_benefits = chat_with_gpt(prompt)
            st.session_state.gpt_response_benefits = remarks_benefits

            # Update the existing data with new user input and GPT response
            existing_data.update({
                "user_benefits": user_benefits,
                "gpt_benefits_remarks": remarks_benefits,
            })

            # Save the updated data back to the file
            save_data(filename, existing_data)
 
    # Display GPT response
    if st.session_state.count >= 4 and st.session_state.gpt_response_benefits:
        st.subheader(translations["alien_feedback"][language])
        st.write(st.session_state.gpt_response_benefits)
 
    #Step 3: Counter to benefits    
    if st.session_state.count >= 4:
        st.subheader(translations["step3_counter_benefits"][language])
        counter_to_benefits= st.text_area(translations["reply_to_feedback"][language], key='counter_to_benefits')
        filename = f"data/{user_name}_data.json"
        if st.button(translations["submit_counter_argument"][language], key='submit_counter') and counter_to_benefits != '':
 
            filename = f"data/{user_name}_data.json"
           
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}
 
            existing_data.update({
            "counter_to_benefits":counter_to_benefits
            })
 
            # Write the updatefilenamed dictionary back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)

    # STEP 4: Examples
    if st.session_state.count >= 5:
        # Load the prompt template from the file
        prompt_template = load_prompt_template(scenario)

        # Display thank you message and examples request
        # st.write(translations["thank_you_response"][language])
        st.subheader(translations["step3_examples"][language])
        user_examples = st.text_area(translations["request_for_examples"][language], key='user_examples')

        filename = f"data/{user_name}_data.json"
        
        if st.button(translations["submit_examples"][language], key='submit_examples') and user_examples != '':
            st.write(translations["waiting_message"][language])

            # Load existing data or create an empty dictionary if file doesn't exist
            existing_data = load_existing_data(filename)

            # Generate the GPT prompt using the loaded template
            prompt = generate_examples_prompt(prompt_template, existing_data, user_examples)

            # Get GPT's response
            remarks_examples = chat_with_gpt(prompt)
            st.session_state.gpt_response_examples = remarks_examples

            # Update the existing data with new examples and GPT response
            existing_data.update({
                "user_examples": user_examples,
                "gpt_examples_remarks": remarks_examples
            })

            # Save the updated data back to the file
            save_data(filename, existing_data)

# Display GPT response
    if st.session_state.count >= 6 and st.session_state.gpt_response_examples:
        # Load the prompt template from the file
        prompt_template = load_prompt_template(scenario)

        st.subheader(translations["alien_feedback"][language])
        st.write(st.session_state.gpt_response_examples)

    #     # STEP 5: Counter to examples
    # if st.session_state.count >= 6:
    #     st.subheader(translations["step5_counter_benefits"][language])
    #     counter_to_benefits_2 = st.text_area(translations["reply_to_feedback_2"][language], key='counter_to_benefits_2')
        
    #     filename = f"data/{user_name}_data.json"
        
    #     if st.button(translations["submit_counter_argument_2"][language], key='submit_counter_2') and counter_to_benefits_2 != '':
    #         st.write(translations["waiting_message"][language])

    #         existing_data = load_existing_data(filename)

    #         # Generate counter to examples prompt
    #         prompt = generate_counter_to_examples_prompt(prompt_template , existing_data, counter_to_benefits_2)
            
    #         # Get GPT's response
    #         remarks_counter = chat_with_gpt(prompt)
    #         st.session_state.gpt_counter_response = remarks_counter

    #         # Update the existing data with the counter response
    #         existing_data.update({
    #             "counter_to_examples": counter_to_benefits_2,
    #             "gpt_counter_response": remarks_counter
    #         })

    #         # Save the updated data back to the file
    #         save_data(filename, existing_data)

    if st.session_state.count >= 6 :  
        existing_data = load_existing_data(filename)
        select_only_user_answers = {
            "Innovation":existing_data["user_examples"],
            "Benefits":existing_data["user_benefits"],
            "Counter to Benefits":existing_data["counter_to_benefits"],
            "Examples":existing_data["user_examples"],
            "Counter to Examples":existing_data["counter_to_benefits"]
            }

        # Generate final evaluation prompt
        prompt = generate_final_evaluation_prompt(prompt_template, select_only_user_answers)
        
        # Get GPT's final evaluation
        final_evaluation = chat_with_gpt(prompt)
        st.session_state.gpt_evaluation = final_evaluation

        # Update the existing data with the final evaluation
        existing_data.update({
            "gpt_evaluation": final_evaluation
        })

        # Save the updated data back to the file
        save_data(filename, existing_data)

 
# Display GPT response
    if st.session_state.count >= 6 and st.session_state.gpt_evaluation:
        st.subheader(translations["alien_evaluation"][language])
        st.write(st.session_state.gpt_evaluation)

    if st.session_state.count >= 6:    
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
            st.session_state.count+=1


    if st.session_state.count >= 7:
        # Collect improvement feedback as text
        improvement_feedback = st.text_input(translations["tell_us_how_to_improve"][language])
        
        # Use radio buttons for satisfaction rating
        satisfaction = st.radio(
            "How satisfied are you with the game?",
            options=["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"]
            )

        not_satisfaction = st.radio(
            "How not satisfied are you with the game?",
            options=["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"]
        )

        if st.button(translations["submit_feedback"][language], key='submit_feedback'):
            filename = f"data/{user_name}_data.json"
            try:
                # Read existing data from file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                existing_data = {}
            
            # Update the dictionary with the feedback data
            existing_data.update({
                "improvement_feedback": improvement_feedback,
                "satisfaction": satisfaction,
                "satisfaction2": not_satisfaction
            })
            
            # Write the updated feedback data back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)

            st.session_state.count += 1
            st.write(st.session_state.count)
            st.balloons()  # Optional: adds a fun balloon animation
            st.markdown(
                "<h2 style='text-align: center; color: #4CAF50;'>Thanks for playing!</h2>",
                unsafe_allow_html=True
            )

        
run()
 
