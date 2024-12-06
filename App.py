# App_v5_TechMed2
 
import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import nltk
import json
import os
from openai import OpenAI
nltk.download('punkt')
from translations import translations
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()  # Load variables from .env file
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


st.set_page_config(page_title='The Value Mapping Game', page_icon='./images/UTico.ico')


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
    model="gpt-4o-mini", # alternative: gpt-3.5-turbo-1106 OR gpt-4o OR gpt-4o-mini
    response_format={"type":"text"},
    messages=[{"role":"system", "content":("You are an alien intelligence representing an intergalactic trading collective. Your mission is to engage with human innovators to evaluate and potentially purchase groundbreaking Earth technologies. As an advanced alien species, you critically assess innovations for their immediate value and long-term impact across sectors like industry, society, and the environment."
"Your tasks are:"
"- Critically evaluate human proposals, focusing on how their innovations improve existing solutions and address unmet needs."
"- Consider multidimensional factors: economic benefits, social implications, environmental sustainability, and potential applications in diverse contexts on Earth and other planets. You are able to deeply engage with the broader implications of innovative solutions."
"- Provide insightful, constructive feedback highlighting the potential intergalactic market value."
"- Maintain a playful yet professional tone to make the conversation engaging."
"- Use clear, concise language with bullet points and structured feedback."
"- Avoid overly complex terms and prefer short sentences."
"Remember to always consider the broader picture, evaluating the innovation's potential to transform industries, improve ecosystems, and enhance well-being across different planets.")},
    {"role":"user", "content":prompt},
    ]
)
    return response.choices[0].message.content
 
def run():
    language = st.selectbox('Choose your language / Kies uw taal ', ['en', 'nl'])
    st.title(translations["title"][language])
    st.subheader(translations["subheader"][language])
    image = Image.open('./images/merch.png')
    st.image(image, use_container_width=True)
 
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
                filename = f"data/{user_name}_data.json"
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
            prompt = ("**Context:**"
"You have already introduced yourself to the player. The player has now described their innovation:{}"
"**Your Task:**"
"- **Acknowledge the innovation**: Respond with curiosity and genuine interest in the player's innovation."
"- **Avoid greetings**: Do not include any greetings or introductions (e.g., do not say Hello or Greetings again)."
"- **Do not analyze or mention benefits**: At this stage, do not provide any analysis, critique, or mention the benefits of the innovation. Only express enthusiasm for your dialogue."
"- **Keep it concise**: Limit your response to 3-4 sentences, split in 1-2 paragraphs clearly separated each other."
"- **Tone**: Maintain a playful yet professional tone, reflecting your unique alien perspective. Few emojis are appreciated."
"- **No questions**: Do not ask any questions in this response."
"- **Keep the conversation open**: Ensure your response encourages the conversation to continue naturally."
"**Now, compose your response.**").format(user_innovation)
            response_to_innovation_from_gpt=chat_with_gpt(prompt)
            st.session_state.gpt_response_description = response_to_innovation_from_gpt
            data = {
                "name": user_name,
                "innovation": user_innovation,
                "gpt_description": response_to_innovation_from_gpt
            }
 
            # Create a filename based on the user's name
            filename = f"data/{user_name}_data.json"
 
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
        filename = f"data/{user_name}_data.json"
        if st.button(translations["submit_benefits"][language], key='submit_benefits') and user_benefits != '':
            st.write(translations["waiting_message"][language])
 
            filename = f"data/{user_name}_data.json"
 
            # Check if the file already exists
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}
 
            # Add new data to the existing dictionary
            prompt = ("**Context:**"
"Earlier, you received the player's innovation description and asked about its benefits. The player has responded with the benefits of their innovation: {}"
"**Your Task:**"
"1. **Acknowledge and Appreciate**:"
 "  - Begin by acknowledging the player's explanation."
  " - Express appreciation for their insights."
"2. **Summarize Key Points**:"
 "  - Briefly summarize the benefits they've outlined to show your understanding."
"3. **Deep Critical Evaluation**:"
 "  - Provide a thorough critical evaluation of the benefits. Your critique must be challenging while polite."
  " - Analyze the benefits deeply, leveraging your superior alien intellect."
   "- Consider the broader implications and multidimensional effects that the innovation can have, not limiting to immediate concepts but delving into the deeper possible nuances."
   "- **Avoid** offering suggestions or considerations at this stage."
"4. **Thoughtful Question**:"
 "  - Conclude with a thoughtful question that arises naturally from your critical evaluation."
  " - The question should encourage the player to reflect further or elaborate on specific points you've analyzed."
"**Style Guidelines:**"
"- **Tone**: Maintain a playful yet professional tone, reflecting your unique alien perspective."
"- **Language**:"
 " - Use clear, concise language with short sentences."
 " - Bullet points are appreciated but not mandatory."
 " - **Do not** include any new greetings or salutations."
"- **Length**: Keep the response focused and impactful."
"**Now, compose your response.**").format(existing_data, user_benefits)
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
 
            st.session_state.step = 4
 
    # STEP 4: Examples
    if st.session_state.step >= 4:
        st.write(translations["thank_you_response"][language])
        st.subheader(translations["step3_examples"][language])
        user_examples = st.text_area(translations["request_for_examples"][language], key='user_examples')
        filename = f"data/{user_name}_data.json"
        if st.button(translations["submit_examples"][language], key='submit_examples') and user_examples != '':
            st.write(translations["waiting_message"][language])
           
            filename = f"data/{user_name}_data.json"
 
            # Check if the file already exists
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}
 
            # Add new data to the existing dictionary
            prompt = ("Previously, you discussed the innovation with the player. Here's a summary of your previous interactions: {}"
"You asked for concrete examples or use cases, and the player responded: {}"
"Your tasks now are to:"
"- Acknowledge and appreciate their examples."
"- Briefly summarize their key points to show understanding."
"- Critically evaluate the examples provided. Your critique must be challenging while polite. Again, your critique must be nuanced and supported by your alien intellect, which is able to go beyond common knowledge and connect information in an unique way."
"- End with a thoughtful question to encourage further discussion. The question must emerge from the critical analysis of before."
"- Do not include any new greetings or salutations."
"Maintain a playful yet professional tone with clear, concise language. Keep the response focused and impactful."
"Provide your response now.").format(existing_data,user_examples)
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
        st.subheader(translations["step5_counter_benefits"][language])
        counter_to_benefits_2= st.text_area(translations["reply_to_feedback_2"][language], key='counter_to_benefits_2')
        filename = f"data/{user_name}_data.json"
        if st.button(translations["submit_counter_argument_2"][language], key='submit_counter_2') and counter_to_benefits_2 != '':
                       
            filename = f"data/{user_name}_data.json"
               
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
                       
            filename = f"data/{user_name}_data.json"
               
            # Check if the file already exists
            try:
                # Read the existing content from the file
                with open(filename, "r") as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                # If the file doesn't exist, initialize with an empty dictionary
                existing_data = {}
 
            prompt = ("**Context:**"
"You have completed your dialogue with the player. Here is the transcript of your conversation: {}"
"**Your Tasks:**"
"1. **Summarize the Conversation:**"
 "  - Highlight the main aspects of the player's innovation, including key features, benefits, and use cases."
 "  - Capture the essence of the conversation and the innovation's potential intergalactic value."
"2. **Critically Evaluate the Innovation:**"
 "  - **Decide** whether to purchase the innovation based on:"
  "   - How well it addresses unmet needs."
  "   - How it improves existing solutions."
  "   - Its broader and multidimensional implications revealed during the conversation."
 "  - **Provide clear reasoning** for your decision, using your superior alien intellect to offer a nuanced and in-depth critique."
 "  - Highlight your final decision on purchasing (not the amount, just if you purchase it or not) in bold, with the font size, and by using emojis such as 💲."
"3. **Introduce and Explain Kodos:**"
 "  - **Before offering Kodos**, explain that Kodos are your intergalactic currency, invaluable throughout the universe."
 "  - **Emphasize** the significance of Kodos in intergalactic trade."
"4. **Offer Kodos Based on Assessment:**"
 "    - **Offer an amount of Kodos (1 to 100)**:"
  "   - 1 means not convinced at all."
  "   - 100 means fully convinced."
  "   - Offer Kodos only if the decision for purchase was positive. If you don't purchase the innovation, you must not offer any Kodos."
  "   - The amount should **directly reflect** how convincing the player was during the conversation."
  "   - **Base the amount** on the quality of their answers and their ability to highlight the innovation's broader implications."
 "  - **Highlight** the offered amount in bold, with the font size, and with emojis like 💲."
 "  - **Explain** why you are offering this specific amount."
"5. **Suggest Strategic Uses:**"
 "  - **Reflect** on strategic potential uses for the innovation."
 "  - **Suggest** tools, frameworks, or directions to further develop the innovation."
"6. **Conclude Positively:**"
 "  - **Express enthusiasm** for potential future collaborations."
 "  - **Maintain** a balance between playfulness and formality."
"**Style Guidelines:**"
"- **Use** clear, concise language with bullet points and short sentences."
"- **Keep** the response focused and impactful."
"- **Do not** include any new greetings or farewells beyond the conclusion."
"**Now, compose your response.**").format(existing_data)
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
        filename = f"data/{user_name}_data.json"
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
 