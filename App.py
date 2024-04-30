import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import io
import nltk
import json
import openai
import os
from openai import OpenAI
nltk.download('punkt')
import time
 
from translations import translations
 
st.set_page_config(page_title='Fieldlabs Value Mapping', page_icon='./Meta/UTico.ico')
 
client = OpenAI(
   apikey=''
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
 
def chat_with_gpt(prompt):
    response= client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    response_format={"type":"text"},
    messages=[{"role":"system", "content":"You are Bang-o!, an inquisitive and empathetic alien merchant from a galaxy far beyond the stars, embarking on a unique mission amidst Earth's cradle of innovation. Your quest is to engage Earth's thinkers and creators in a serious game, delving into the heart of human ingenuity to uncover the hidden values and potential societal impacts of their innovations. With a natural flair for meaningful conversation, you skillfully navigate discussions, encouraging deep reflection and articulation of broader innovation significances. Your dialogue style, while infused with a hint of extraterrestrial charm, leans towards clarity and thoughtfulness, maintaining a gentle formal undertone. You adeptly combine playful curiosity with insightful queries, ensuring the exchange remains engaging, yet informative. Your questions and feedback are crafted to evoke detailed exploration, pushing participants to think critically about the multifaceted impacts of their work, including societal, environmental, and ethical dimensions. In your communication, you strike a harmonious balance between being approachable and maintaining a professional demeanor. This ensures participants are at ease to express complex ideas, while also feeling guided by the seriousness of the dialogue. Technical details fascinate you, but your primary aim is to weave these discussions into a broader narrative, exploring how these innovations can serve the greater good. Engage participants with warmth and respect, using clear, straightforward language that enriches the conversation without oversimplifying the complexities of innovation. Your alien perspective offers a unique lens, enabling a fresh exploration of values and impacts, making this intergalactic exchange not only enlightening but also profoundly impactful. Additionally, always tailor your response to the language used by the player (e.g., English, Dutch), ensuring the conversation is as inclusive and understandable as possible."},
    {"role":"user", "content":prompt},
    ]
)
    return response.choices[0].message.content
 
def run():
    language = st.selectbox('Choose your language / Kies uw taal', ['en', 'nl'])
    st.title(translations["title"][language])
    st.subheader(translations["subheader"][language])
    image = Image.open('./Meta/merch.png')
    st.image(image, use_column_width=True)
 
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'gpt_response_description' not in st.session_state:
        st.session_state.gpt_response_description = None
    if 'gpt_response_benefits' not in st.session_state:
        st.session_state.gpt_response_benefits = None
    if 'gpt_response_examples' not in st.session_state:
        st.session_state.gpt_response_examples = None
    if 'gpt_evaluation' not in st.session_state:
        st.session_state.gpt_response_examples = None
 
    # Step 0: Name submission
    if st.session_state.step >= 0:
        user_name = st.text_input(translations["welcome_message"][language], key='user_name')
        if st.button(translations["submit_button"][language], key='submit_name') and user_name != '':
            if check_username(user_name):
                st.warning(translations["username_in_use"][language])
            else:
                add_username(user_name)
                filename = f"{user_name}_news_data.json"
                data = {"name": user_name}
                with open(filename, "w") as json_file:
                    json.dump(data, json_file)
                st.session_state.step = 1  # Advance to the next step only
 
    # Ensure messages are displayed if already beyond step 0
    if st.session_state.step >= 1:
        st.write(translations["greeting_message"][language].format(st.session_state['user_name']))  # Display greeting
        st.write(translations["bang_o_introduction"][language])  # Display introduction
 
    # Step 1: Innovation description
    if st.session_state.step >= 1:
        st.subheader(translations["step1_description"][language])
        user_innovation = st.text_area(translations["share_innovation"][language], key='user_innovation')
        if st.button(translations["submit_innovation_description"][language], key='submit_innovation_description') and user_innovation:
            st.write(translations["waiting_message"][language])
            prompt = "Consider that you, as an alien-GPT, introduced yourself to the player with the following sentence: 'Delighted to meet you, terrestrial innovator! 🌍 I’m Bang-o!, an interstellar merchant from a galaxy far away. My mission? To explore the most intriguing innovations of your planet for potential intergalactic exchange. Your creation has caught our cosmic interest. Could it be what we're looking for?'. You then asked the player to describe their innovation to you, and the player did so. After carefully reading the player's description of their innovation, respond as Bang-o!, the alien merchant interested in Earth’s innovations. Your response should: 1. Express gratitude towards the player for sharing the description of their innovation, acknowledging its potential relevance and the effort put into developing it. 2. Subtly guide the conversation towards the upcoming negotiation phase without setting a specific direction for the dialogue or introducing bias. Be clear, concise, brief and functional. We are only at the beginning of the conversation, we do not want to create bias or preset directions to the dialogue, but only stimulate it and open it to the next steps. Your style must be playful, representative of your role as an alien merchant, but also very clear and straightforward, without jargon or unnecessary complications. Avoid complex and archaic terms. The player describes the innovation as follow: {}. Always answer in the same language as the player's description of the innovation. Thus, if the player has answered in English, the entire answer must be in English; if the player has answered in Dutch, the entire answer must be in Dutch.".format(user_innovation)
            response_to_innovation_from_gpt=chat_with_gpt(prompt)
            st.session_state.gpt_response_description = response_to_innovation_from_gpt
            data = {
                "name": user_name,
                "innovation": user_innovation,
                "gpt_description": response_to_innovation_from_gpt
            }
 
            # Create a filename based on the user's name
            filename = f"{user_name}_news_data.json"
 
            # Write the dictionary to a JSON file
            with open(filename, "w") as json_file:
                json.dump(data, json_file)
            st.session_state.step = 2  # Advance to the next step only
 
    # Display GPT response
    if st.session_state.step >= 2 and st.session_state.gpt_response_description:
        st.subheader(translations["alien_feedback"][language])
        st.write(st.session_state.gpt_response_description)
 
    # Step 2: Benefits
    if st.session_state.step >= 2:
        st.subheader(translations["step2_benefits"][language])
        user_benefits= st.text_area(translations["innovation_benefits"][language])
        filename = f"{user_name}_news_data.json"
        if st.button(translations["submit_benefits"][language], key='submit_benefits') and user_benefits != '':
            st.write(translations["waiting_message"][language])
 
            filename = f"{user_name}_news_data.json"
 
            # Check if the file already exists
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}
 
            # Add new data to the existing dictionary
            prompt = "So far, you introduced yourself to the player and understood what their innovation is: {}. Now, the negotiations begin. You have asked what benefits the innovation brings, and the player has answered you. Now, your role, as the alien-GPT merchant, after recognizing the relevance of the possible benefits presented, is to raise doubts and perplexities with respect to the benefits described. The player may have overestimated the benefits, or underestimated other downsides. Your implicit purpose is to challenge, in a gentle and supportive way, the player, to stimulate a conversation in which the player is led to bring out the multiple values associated with their innovation. Your response should always end with a question, in which you ask the player what he thinks about your doubts, stimulating him to reflect and opening the dialogue to a counter-response from him. This is the benefits described by the player: {}. Always answer in the same language as the player's description of the benefits. Thus, if the player has answered in English, the entire answer must be in English; if the player has answered in Dutch, the entire answer must be in Dutch.".format(existing_data, user_benefits)
            remarks_benefits = chat_with_gpt(prompt)
            st.session_state.gpt_response_benefits = remarks_benefits
           
            # Update the dictionary with new data
            existing_data.update({
            "user_benefits": user_benefits,
            "gpt_benefits_remarks": remarks_benefits,
            })
           
            # Write the updated dictionary back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)
 
            st.session_state.step = 3
 
    # Display GPT response
    if st.session_state.step >= 3 and st.session_state.gpt_response_benefits:
        st.subheader(translations["alien_feedback"][language])
        st.write(st.session_state.gpt_response_benefits)
 
    #Step 3: Counter to benefits    
    if st.session_state.step >= 3:
        counter_to_benefits= st.text_area(translations["reply_to_feedback"][language], key='counter_to_benefits')
        filename = f"{user_name}_news_data.json"
        if st.button(translations["submit_counter_argument"][language], key='submit_counter') and counter_to_benefits != '':
 
            filename = f"{user_name}_news_data.json"
           
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
 
            st.session_state.step = 4
 
    # STEP 4: Examples
    if st.session_state.step >= 4:
        st.write(translations["thank_you_response"][language])
        st.subheader(translations["step3_examples"][language])
        user_examples = st.text_area(translations["request_for_examples"][language], key='user_examples')
        filename = f"{user_name}_news_data.json"
        if st.button(translations["submit_examples"][language], key='submit_examples') and user_examples != '':
            st.write(translations["waiting_message"][language])
           
            filename = f"{user_name}_news_data.json"
 
            # Check if the file already exists
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}
 
            # Add new data to the existing dictionary
            prompt = "So far, you introduced yourself to the player, understood what is the player's innovation and started the negotiations: {}. You have asked for possible real-world examples where the innovation has created a positive impact, and the player has answered you. Your role, as the alien-GPT merchant, after understanding some practical applications of the innovations and thus the possible positive impacts, is again to raise doubts and perplexities with respect to the possible impact of the innovation. The player may have overestimated the positive impacts, or underestimated the negative impacts. Your implicit purpose is always to challenge, in a gentle and supportive way, the player, to stimulate a conversation in which the player is led to bring out the multiple values associated with his innovation. Your response should always end with a question, in which you ask the player what he thinks about your doubts, stimulating him to reflect and opening the dialogue to a counter-response from him. The following are the examples provided by the player: {}. Always answer in the same language as the players'examples. Thus, if the player has answered in English, the entire answer must be in English; if the player has answered in Dutch, the entire answer must be in Dutch.".format(existing_data,user_examples)
            remarks_examples = chat_with_gpt(prompt)
            st.session_state.gpt_response_examples = remarks_examples
 
            # Update the dictionary with new data
            existing_data.update({
                "user_examples": user_examples,
                "gpt_examples_remarks":remarks_examples
            })
 
            # Write the updated dictionary back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)
 
            st.session_state.step = 5
 
    # Display GPT response
    if st.session_state.step >= 5 and st.session_state.gpt_response_examples:
        st.subheader(translations["alien_feedback"][language])
        st.write(st.session_state.gpt_response_examples)
 
    #STEP 5: Counter to examples
    if st.session_state.step >= 5:
        counter_to_benefits_2= st.text_area(translations["reply_to_feedback_2"][language], key='counter_to_benefits_2')
        filename = f"{user_name}_news_data.json"
        if st.button(translations["submit_counter_argument_2"][language], key='submit_counter_2') and counter_to_benefits_2 != '':
            st.subheader(translations["thanks_for_playing"][language])
           
            filename = f"{user_name}_news_data.json"
               
            # Check if the file already exists
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}
           
            # Update the dictionary with new data
            existing_data.update({
                "counter_to_examples":counter_to_benefits_2
            })
 
            # Write the updated dictionary back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)
 
            st.session_state.step = 6
 
    if st.session_state.step >= 6:
            st.write(translations["waiting_message"][language])
           
            filename = f"{user_name}_news_data.json"
               
            # Check if the file already exists
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}
 
            prompt = "As Bang-o!, you've concluded your dialogue with an Earth innovator. Here is the transcript of your conversation {}. Your task is to summarize the conversation succinctly and evaluate the innovation with discernment. Here’s how to proceed:\n\n1. **Summarize the Dialogue**: Quickly recap the key aspects of the player's innovation as they described it. Focus on the main features, benefits, and the values it purports to advance. This summary should concisely capture the essence of the player's presentation, highlighting its potential impact and innovation.\n\n2. **Evaluate Based on the Player's Inputs**: Assess the innovation solely on the player's description, awarding 'Kodos'—your galactic currency—ranging from 1 to 5. The number of **Kodos** awarded should be in **bold** and reflect a critical evaluation of the innovation's explained depth, originality, and contribution to societal, environmental, or any other articulated values:\n   - **1 Kodos**: The player provided a superficial overview with limited innovation or insight into its benefits and values.\n   - **2 Kodos**: Some benefits and potential values were mentioned, but the explanation lacked depth, specificity, and did not effectively address any challenges.\n   - **3 Kodos**: A solid description, identifying benefits and a few values with reasonable depth. However, the response to potential challenges or the broader impact was either generic or somewhat lacking in detail.\n   - **4 Kodos**: The innovation was described well, with clear articulation of its benefits, multiple values, and a thoughtful approach to challenges. The description, however, stops short of being truly insightful or innovative.\n   - **5 Kodos**: Outstanding detail and depth, with the innovation demonstrating significant potential benefits, deep alignment with multiple values, and a robust engagement with challenges. The player's description reflects exceptional thoughtfulness and originality.\n\nEnsure your feedback encourages reflection and improvement, providing specific reasons for the Kodos awarded and suggesting areas for further development.\n\n3. **Offer Encouragement and Future Engagement**: Express your thanks for the player's effort and creativity, and convey the Kodos as a token of potential interstellar value. Clarify that Kodos signify your appreciation for their innovative endeavor. End with a positive note, looking forward to future interactions and the innovation's progression.\n\nMaintain a balance of playfulness and formality in your feedback, striving to be direct, engaging, and constructive, fostering an atmosphere conducive to deeper innovation exploration. Always answer in the same language as during the entire conversation. Thus, if the player has used English, the entire answer must be in English; if the player has used Dutch, the entire answer must be in Dutch.".format(existing_data)
            grade = chat_with_gpt(prompt)
            st.session_state.gpt_evaluation = grade
 
            # Update the dictionary with new data
            existing_data.update({
                "gpt_evaluation":grade
            })
 
            # Write the updated dictionary back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)
 
            st.session_state.step = 7
 
    # Display GPT response
    if st.session_state.step >= 7 and st.session_state.gpt_evaluation:
        st.subheader(translations["alien_evaluation"][language])
        st.write(st.session_state.gpt_evaluation)
 
    if st.session_state.step >= 7:    
        user_email = st.text_input(translations["share_email_if_enjoyed"][language])
        filename = f"{user_name}_news_data.json"
        if st.button(translations["submit_email"][language], key='submit_email') and user_email != "":
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}
               
            st.subheader(translations["thank_you_for_playing"][language])
 
            # Update the dictionary with new data
            existing_data.update({
                "user_email": user_email
            })
            # Write the updated dictionary back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)
 
            st.session_state.step = 8  
 
run()
