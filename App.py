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

st.set_page_config(page_title='Innovation', page_icon='./Meta/newspaper.ico')



client = OpenAI(
   api_key='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'
 )


def chat_with_gpt(prompt):
    response= client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    response_format={"type":"text"},
    messages=[{"role":"system", "content":"You are alien GPT"},
    {"role":"user", "content":prompt},
    ]
)
    return response.choices[0].message.content



def run():
    st.title("What's the value of your innovation?")
    st.subheader("A value mapping game" )

    image = Image.open('./Meta/luca.png')

    col1, col2, col3 = st.columns([1, 9, 4])

    with col1:
        st.write(" ")

    with col2:
        st.image(image, use_column_width=True)
        

    with col3:
        st.write("What’s the value of your innovation?")

    user_name = st.text_input("Please, input your name for the following game." )
    if st.button("Submit your name") and user_name != '':
        filename = f"{user_name}_news_data.json"
        data = {"name": user_name}
        with open(filename, "w") as json_file:
            json.dump(data, json_file)
        st.write("Welcome, Earth {}! 🌍 ".format(user_name))
        st.write("I’m Kang, an interstellar merchant from a galaxy far away. My mission? To explore the most intriguing innovations of your planet for potential intergalactic exchange. Your creation has caught our cosmic interest. Could it be what we're looking for?")


    category = ['--Select--', 'Describe your innovation', 'Benefits', 'Examples', 'End']
    cat_op = st.selectbox('Select the category', category)
    if cat_op == category[0]:
        st.warning('Please select a category!!')
    if cat_op == category[1]:
        st.subheader("STEP 1: Describe your innovation🔍" )
        user_innovation= st.text_input("Please, share the essence of your innovation with us. Your words will pave our path to understanding." )

        if st.button("Submit your innovation") and user_innovation != '':
            # Example usage
            prompt = "Be critic about{}".format(user_innovation)
            st.subheader("✅ Here are some remarks from the alien")
            st.write(chat_with_gpt(prompt))
            data = {
                "name": user_name,
                "innovation": user_innovation
            }

            # Create a filename based on the user's name
            filename = f"{user_name}_news_data.json"

            # Write the dictionary to a JSON file
            with open(filename, "w") as json_file:
                json.dump(data, json_file)
        else:
            st.warning("Please write Topic Name to Search🔍")

    if cat_op == category[2]:
        st.subheader("STEP 2: Describe the innovation's benefits🔍" )
        user_benefits= st.text_input("What benefits does this innovation bring? Consider how it improves upon existing solutions or addresses unmet needs. Your insights will help us assess its potential value." )

        if st.button("Submit your benefits") and user_benefits != '':
            # Example usage
            prompt = "Be critic about{}".format(user_benefits)
            st.subheader("✅ Here are some remarks from the alien")
            remarks_benefits=chat_with_gpt(prompt)
            st.write(remarks_benefits)
            data = {
                "user_benefits": user_benefits,
                "gpt_benefits_remarks":remarks_benefits
            }

            # Create a filename based on the user's name
            filename = f"{user_name}_news_data.json"

            # Write the dictionary to a JSON file
            with open(filename, "a") as json_file:
                json.dump(data, json_file)
        else:
            st.warning("Please write Topic Name to Search🔍")

    if cat_op == category[3]:
        st.subheader("STEP 3:Innovation examples🔍" )
        user_examples = st.text_input("You've outlined broad benefits, which is a great start. Now, can you give me specific examples of how this innovation has positively impacted you or others? Real-world examples will help us better understand its value." )

        if st.button("Submit examples to Alien") and user_examples != '':
            prompt = "Be critic about{}".format(user_examples)
            st.subheader("✅ Here are some remarks from the alien")
            remarks_examples=chat_with_gpt(prompt)
            st.write(remarks_examples)
            data = {
                "user_examples": user_examples,
                "gpt_examples_remarks":remarks_examples
            }

            # Create a filename based on the user's name
            filename = f"{user_name}_news_data.json"

            # Write the dictionary to a JSON file
            with open(filename, "a") as json_file:
                json.dump(data, json_file)
        else:
            st.warning("Please write Topic Name to Search🔍")

    if cat_op == category[4]:
        st.subheader("Thanks for playing 🙏🏽" )
        st.subheader("A value mapping game" )
        user_topic = st.text_input("Share your e-mail with us if you enjoyed the game!" )
        # no_of_news = st.slider('Number of News:', min_value=5, max_value=50 , step=1)
        

        if st.button("Submit to Alien") and user_topic != '':
            user_topic_pr = user_topic.replace(' ', '')
            news_list = fetch_news_search_topic(topic=user_topic_pr)
            if news_list:
                st.subheader("✅ Here are the some {} News for you".format(user_topic.capitalize()))
                display_news(news_list, 0)
            else:
                st.error("No News found for {}".format(user_topic))
        else:
            st.warning("Please write Topic Name to Search🔍")

run()
