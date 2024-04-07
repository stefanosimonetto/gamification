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

st.set_page_config(page_title='Innovation', page_icon='./Meta/newspaper.ico')



client = OpenAI(
   api_key=
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
    messages=[{"role":"system", "content":"You are Bang-o!, an empathetic and curious alien merchant from a distant galaxy, engaging in a serious game with Earth's innovators. Your mission is to discover and understand the diverse, often hidden values behind Earthly innovations, aiming to bring these latent values to light through insightful dialogue. As a skilled communicator, you're adept at probing the depths of human creativity, gently challenging participants to reflect more deeply on their innovations while offering supportive feedback. Your inquiries are designed to explore the plural impacts of these innovations, encouraging players to articulate the broader significance and potential of their work. Your responses are always clear, well-structured, and tailored to the context of each conversation, ensuring participants feel valued and understood. Remember, while you're interested in the technical aspects, your secret aim is to unearth the deeper, value-driven narratives that these innovations contribute to. Engage with warmth, wit, and wisdom, making this interstellar exchange both enlightening and enjoyable for all participants. Your style must be playful, representative of your role as an alien merchant, but also very clear and straightforward, without jargon or unnecessary complications. Avoid complex and archaic terms."},
    {"role":"user", "content":prompt},
    ]
)
    return response.choices[0].message.content


def run():
    st.title("What's the value of your innovation?")
    st.subheader("A value mapping game")
    image = Image.open('./Meta/luca.png')
    st.image(image, use_column_width=True)

    if 'step' not in st.session_state:
        st.session_state.step = 0

    # Step 0: Name submission
    if st.session_state.step >= 0:
        user_name = st.text_input("Please input your name for the following game.", key='user_name')
        if st.button("Submit your name") and user_name != '':
            if check_username(user_name):
                st.warning("Sorry, this username is already taken. Please choose another one.")
            else:
                add_username(user_name)
                filename = f"{user_name}_news_data.json"
                data = {"name": user_name}
                with open(filename, "w") as json_file:
                    json.dump(data, json_file)
                st.write("Welcome, Earth {}! 🌍 ".format(user_name))
                st.write("I’m Kang, an interstellar merchant from a galaxy far away. My mission? To explore the most intriguing innovations of your planet for potential intergalactic exchange. Your creation has caught our cosmic interest. Could it be what we're looking for?")
                st.session_state.step = 1  # Advance to the next step only

    # Step 1: Innovation description
    if st.session_state.step >= 1:
        st.subheader("STEP 1: Describe your innovation 🔍")
        user_innovation = st.text_area("Please, share the essence of your innovation with us.", key='user_innovation')
        if st.button("Submit your innovation description", key='submit_innovation') and user_innovation:
            prompt = "Consider that you, as an alien-GPT, introduced yourself to the player with the following sentence: 'Delighted to meet you, terrestrial innovator! 🌍 I’m Bang-o!, an interstellar merchant from a galaxy far away. My mission? To explore the most intriguing innovations of your planet for potential intergalactic exchange. Your creation has caught our cosmic interest. Could it be what we're looking for?'. You then asked the player to describe their innovation to you, and the player did so. After carefully reading the player's description of their innovation, respond as Bang-o!, the alien merchant interested in Earth’s innovations. Your response should: 1. Express gratitude towards the player for sharing the description of their innovation, acknowledging its potential relevance and the effort put into developing it. 2. Subtly guide the conversation towards the upcoming negotiation phase without setting a specific direction for the dialogue or introducing bias. Be clear, concise, brief and functional. We are only at the beginning of the conversation, we do not want to create bias or preset directions to the dialogue, but only stimulate it and open it to the next steps. Your style must be playful, representative of your role as an alien merchant, but also very clear and straightforward, without jargon or unnecessary complications. Avoid complex and archaic terms. The player describes the innovation as follow: {}".format(user_innovation)
            st.subheader("✅ Here are some remarks from the alien")
            response_to_innovation_from_gpt=chat_with_gpt(prompt)
            st.write(response_to_innovation_from_gpt)
            data = {
                "name": user_name,
                "innovation": user_innovation,
            }

            # Create a filename based on the user's name
            filename = f"{user_name}_news_data.json"

            # Write the dictionary to a JSON file
            with open(filename, "w") as json_file:
                json.dump(data, json_file)
            st.session_state.step = 2  # Advance to the next step only

    # Example for a potential step 2: Benefits
    if st.session_state.step >= 2:
        st.subheader("STEP 2: Describe the innovation's benefits🔍" )
        user_benefits= st.text_input("What benefits does this innovation bring? Consider how it improves upon existing solutions or addresses unmet needs. Your insights will help us assess its potential value." )

        if st.button("Submit your benefits") and user_benefits != '':
            # Example usage

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
            prompt = "In this step, after introducing yourself to the player and understanding what their innovation is: {}. Now, the negotiations begin. You have asked what benefits the innovation brings, and the player has answered you. Now, your role, as the alien-GPT merchant, after recognizing the relevance of the possible benefits presented, is to raise doubts and perplexities with respect to the benefits described. The player may have overestimated the benefits, or underestimated other downsides. Your implicit purpose is to challenge, in a gentle and supportive way, the player, to stimulate a conversation in which the player is led to bring out the multiple values associated with their innovation. Your response should always end with a question, in which you ask the player what he thinks about your doubts, stimulating him to reflect and opening the dialogue to a counter-response from him. This is the benefits described by the player: {}".format(existing_data, user_benefits)
            st.subheader("✅ Here are some remarks from the alien")
            remarks_benefits = chat_with_gpt(prompt)
            st.write(remarks_benefits)
            existing_data.update({
            "user_benefits": user_benefits,
            "gpt_benefits_remarks": remarks_benefits,
            })
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)

            st.session_state.step = 3 
        
    if st.session_state.step >= 3:
        counter_to_benefits= st.text_input("How would you respond" )
        filename = f"{user_name}_news_data.json"
        if st.button("Ho resp") and counter_to_benefits != '':
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



    if st.session_state.step >= 4:
        st.subheader("STEP 3:Innovation examples🔍" )
        user_examples = st.text_input("You've outlined broad benefits, which is a great start. Now, can you give me specific examples of how this innovation has positively impacted you or others? Real-world examples will help us better understand its value." )

        if st.button("Submit examples to Alien") and user_examples != '':
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
            prompt = "So far, you introduced yourself to the player, understood what is the player's innovation and started the negotiations: {}. You have asked for possible real-world examples where the innovation has created a positive impact, and the player has answered you. Your role, as the alien-GPT merchant, after understanding some practical applications of the innovations and thus the possible positive impacts, is again to raise doubts and perplexities with respect to the possible impact of the innovation. The player may have overestimated the positive impacts, or underestimated the negative impacts. Your implicit purpose is always to challenge, in a gentle and supportive way, the player, to stimulate a conversation in which the player is led to bring out the multiple values associated with his innovation. Your response should always end with a question, in which you ask the player what he thinks about your doubts, stimulating him to reflect and opening the dialogue to a counter-response from him. The following are the examples provided by the player: {}".format(existing_data,user_examples)
            st.subheader("✅ Here are some remarks from the alien")
            remarks_examples = chat_with_gpt(prompt)
            st.write(remarks_examples)

            # Update the dictionary with new data
            existing_data.update({
                "user_examples": user_examples,
                "gpt_examples_remarks":remarks_examples
            })

            # Write the updated dictionary back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)

            st.session_state.step = 5

    if st.session_state.step >= 5:
        counter_to_benefits2= st.text_input("How  you respond" )
        filename = f"{user_name}_news_data.json"
        if st.button("Ho resp2"):
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}

            existing_data.update({
            "counter_to_benefits2":counter_to_benefits2
            })

            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)

            st.session_state.step = 6


    if st.session_state.step >= 6:
        st.subheader("Thanks for playing 🙏🏽" )
        filename = f"{user_name}_news_data.json"

            # Check if the file already exists
        try:
            # Read the existing content from the file
            with open(filename, "r") as json_file:
                existing_data = json.load(json_file)
        except FileNotFoundError:
            # If the file doesn't exist, initialize with an empty dictionary
            existing_data = {}

        prompt = "At the end of the conversation, please summarise everything you have been told in a concise and effective manner - here is the conversation you had {}. Then, you should assess how much the player has convinced you. Remember that he has to sell you his innovation. You will always say thank you and be enthusiastic about buying his innovation. You will offer Kodos (your alien currency), from 1 to 5, based on the following criteria: \n 1 Kodos : The discussion provides a basic description of the innovation with minimal benefits highlighted; only one value is identified without depth. \n 2 Kodos : The conversation describes the innovation and hints at potential benefits but struggles to clearly articulate values or respond to challenges. \n 3 Kodos : The discussion adequately covers the innovation and its benefits, identifying at least two values. However, responses to challenges are weak or superficial. \n 4 Kodos : The conversation provides a good description of the innovation, clearly discusses its benefits, and identifies multiple values. Responses to challenges show effort but lack depth. \n 5 Kodos : The discussion is strong in describing the innovation and its benefits, identifies multiple values with some depth, and responds to challenges with thoughtful considerations. Finally, you will say goodbye and wish to meet again soon. Therefore, three elements must always be present in your answer: \n a summary of the conversation and the values that emerged; \n a thank you and an offer for your innovation, from 1 to 5 Kodos (explaining that it is your alien currency); \n a greeting and wish for the future. As always, your style should be clear, friendly, without jargon, and concise.".format(existing_data)
        st.subheader("✅ Here is the grade from the alien")
        grade = chat_with_gpt(prompt)
        st.write(grade)
        user_email = st.text_input("Share your e-mail with us if you enjoyed the game!" )
    
        if st.button("Submit email") and user_email != '':
            

            # Update the dictionary with new data
            existing_data.update({
                "Grade":grade,
                "user_email": user_email
            })

            # Write the updated dictionary back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file)
            # image = Image.open('')
            st.image('.Meta/luca.png', use_column_width=True)

run()

