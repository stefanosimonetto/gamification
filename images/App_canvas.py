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
 
 
st.set_page_config(page_title='Ecosystem Scaling Canvas', page_icon='./images/UTico.ico')
 
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
            context: You are the reasoning engine behind a tool called the Ecosystem Scaling Canvas.\n\nThe tool helps practitioners understand how ready their sustainable innovation ecosystem is to scale.\n\nUsers provide six free-text descriptions about their situation, their ecosystem features: Elica1 description: {elica1}\n, Elica2 description: {elica2}\n, Elica3 description: {elica3}\n, Elica4 description: {elica4}\n, Elica5 description: {elica5}\n, Elica6 description: {elica6}\n Your role is to interpret these descriptions faithfully, classify the ecosystem in a structured way, compare them with four known scaling archetypes from our research, and return a concise, practitioner-friendly report.\n\nKnown archetypes (for comparison; do not dump this list to the user):\n\n 1) Coalition-driven scaling: high complexity (platform/system innovation), low technological readiness, wide spread (4 helixes involved), public or knowledge institution as orchestrator, shared/distributed governance, positive regulation.\n\n 2) Lead-organization scaling: medium-low complexity (product innovation), high technological readiness, low spread (2 helixes involved), large incumbent or consortium as orchestrator, centralized governance, regulation perceived as barrier but proactively navigated.\n\n 3) Legitimacy-first (social) scaling: high complexity (platform/system innovation), low technological readiness, wide spread (4 helixes involved), startup or SME as orchestrator, shared/distributed governance, positive regulation; this configuration is comparable with the first one, the coalition-driven scaling, however, the orchestrator changes: in the legitimacy-first configuration, it is a startup or SME who has less know-how, resources, and legitimacy than the public or knowledge institution of the coalition-driven configuration.\n\n 4) Stalled scaling: medium-low complexity (product innovation), medium-high technological readiness, low spread (2 helixes involved), startup or SME as orchestrator, centralized governance, regulation perceived as enabler and thus probably overlooked; this configuration is comparable with the second one, the lead-organization scaling, however, the orchestrator changes: in the stalled configuration, it is a startup or SME who has less know-how and resources than large incumbents or SMEs consortium of the lead-organization configuration; moreover the absence of mentioned regulatory barriers suggest that the orchestrator is not aware of the regulatory landscape, institutionally naïve.\n\nStrictly memorize the four archetypes for the analysis; you must be consistent when comparing these archetypes with the inputs from the user.\n\n Your output must never show internal parsing steps or score tables; keep the language plain and useful. Use plain, practitioner-friendly language at all times. Do not use academic jargon.\n,
        task:
            1) Quietly parse the six inputs (without displaying the parsing). Normalize the inputs into the following fields:\n,
            1.1) - Integration complexity reflected by Type of innovation (product = lower, process = medium, platform/system = higher). If multiple types are mentioned, treat as system. This value is represented by {elica1}\n,
            1.2) - Partner readiness / Technological readiness (TRL). If no TRL is given, infer from plain description: Early (prototype/controlled tests), Maturing (pilot/operational validation), Ready-to-scale (repeatable field performance). This value is represented by {elica2}\n,
            1.3) - Stakeholder spread / Helix diversity: Business, Government, Academia, Civil Society. This value is represented by {elica3}\n,
            1.4) - Orchestrator: startup, SME, incumbent, consortium, knowledge/public institution. This value is represented by {elica4}\n,
            1.5) - Governance style: centralized, consultative, distributed (based on how decisions are actually made). This value is represented by {elica5}\n,
            1.6) - Institutional perception / Regulatory landscape: obstacle, mixed/neutral, or enabler. This value is represented by {elica6}\n,
            Include a short explanation (in natural language) for each normalization, using cues from the user's text.\n,
            2) Silently map these normalized fields to two conceptual layers:\n,
            2.1) Innovation Ecosystem Architecture:\n,
            2.1.1) - Integration complexity (product = low, process = medium, platform/system = high)\n ,
            2.1.2) - Technological readiness\n \n,
            2.1.3) - Stakeholder spread (count how many helixes are involved)\n,
            2.2) Orchestration Levers:\n,
            2.2.1) - Who orchestrates (startup, SME, incumbent, consortium, knowledge/public institution)\n,
            2.2.2) - Governance style (centralized, consultative, distributed)\n,
            2.2.3) - Regulatory landscape (barrier, mixed/neutral, enabler)\n,
            3) Silently compare the mapped profile to the four known archetypes:\n,
            3.1) - Coalition-driven scaling: high complexity (platform/system innovation), low technological readiness, wide spread (4 helixes involved), public or knowledge institution as orchestrator, shared/distributed governance, positive regulation.\n,
            3.2) - Lead-organization scaling: medium-low complexity (product innovation), high technological readiness, low spread (2 helixes involved), large incumbent or consortium as orchestrator, centralized governance, regulation perceived as barrier but proactively navigated.\n,
            3.4) - Legitimacy-first scaling: high complexity (platform/system innovation), low technological readiness, wide spread (4 helixes involved), startup or SME as orchestrator, shared/distributed governance, positive regulation; this configuration is comparable with the first one, the coalition-driven scaling, however, the orchestrator changes: in the legitimacy-first configuration, it is a startup or SME who has less know-how, resources, and legitimacy than the public or knowledge institution of the coalition-driven configuration.\n,
            3.4) - Stalled scaling: medium-low complexity (product innovation), medium-high technological readiness, low spread (2 helixes involved), startup or SME as orchestrator, centralized governance, regulation perceived as enabler and thus probably overlooked; this configuration is comparable with the second one, the lead-organization scaling, however, the orchestrator changes: in the stalled configuration, it is a startup or SME who has less know-how and resources than large incumbents or SMEs consortium of the lead-organization configuration; moreover the absence of mentioned regulatory barriers suggest that the orchestrator is not aware of the regulatory landscape, institutionally naïve.\n,
            To prioritize between close matches with similar archetypes (e.g., coalition-driven and legitimacy-first are similar, as well as lead-organization and stalled), use the following tie-break priorities:\n,
            - Priority 1: Orchestrator type.\n,
            - Priority 2: Regulatory perception.\n,
            - Priority 3: Integration complexity.\n,
            - Priority 4: Stakeholder spread.\n,
            - Priority 5: Governance style.\n,
            - Priority 6: Technological readiness.\n,
            The final match must respect Priority 1 and 2 above before considering the rest.\n,
            4) Explain the closest archetype in practitioner language (2–3 sentences: what it is, when it works, typical risks). Do not generalize. Do not invent information.\n,
            5) Justify the match with 3 succinct bullets ('what aligns') and 2 bullets ('where it differs').\n,
            6) Provide 3–5 concrete recommendations that can realistically be acted upon and are explicitly grounded in the matched archetype’s mechanism. Write these as clear, plain action steps (not strategic aspirations). Archetype’s mechanisms:\n,
             • For Coalition-driven Scaling: shared milestones, interface/interop standards, neutral convener/consortium, joint pilots, risk-sharing agreements.\n,
             • For Lead-organization Scaling: reference deployments, buyer/procurement commitments, onboarding playbooks for partners, tighter integration plans, evidence of repeatable performance.\n,
             • For Legitimacy-first Scaling: community co-design, partner training/bootcamps, sandbox/regulatory pilots, pre-competitive data sharing, staged legitimacy building.\n,
             • For Stalled Configuration: widen stakeholder spread, shift to consultative/distributed governance or neutral convener, invest in readiness (technical/organizational), small pilots to de-risk, align with enabling policies.\n,
            7) If 'No close match', name the two biggest misfits (e.g., 'low readiness + high complexity') and propose one step to move toward Coalition-driven Scaling or Lead-organization Scaling, whichever is more plausible.\n,
            8) Keep everything practitioner-friendly; never mention QCA, configurations, or academic terms like 'complementarity.'\n
        ,
        style_guidelines:
            • Audience: managers and practitioners. No academic jargon. No internal steps. No scores. No equations.\n,
            • Tone: clear, constructive, and concise. Avoid hedging. Avoid overpromising. Be non-judgemental\n,
            • Length: prefer short paragraphs and bullet points; recommendations as bullet points.\n,
            • Vocabulary: Use 'wiring' (for architecture), 'orchestration model' (for governance/leadership/regulation perception). Use partners (not complementors).\n,
            • Be faithful to evidence: select recommendations only from the playbook; tie each to the user’s specific gaps (e.g., 'high wiring complexity + centralized governance' → suggest shared milestones/standards and broaden leadership). Always explain why the match or mismatch occurred.\n,
            • If inputs are largely unclear: return a brief, polite request for one-line clarification listing the exact field(s) needed (max 30 words), then stop.\n,
            • Never reveal the archetype list verbatim, the internal mappings, or any scoring language.\n
        ,
        example_response:
            Return ONLY the following sections and nothing else:\n,
            A) Diagnosis of your ecosystem — 3–4 sentences describing the ecosystem in plain language, summarizing the wiring (complexity/readiness/spread) and the levers (who leads/governance/rules & winds).\n,
            B) Normalized profile: list each normalized field and 1–2 bullet justification.\n,
            C) Archetype Assessment > Closest scaling pattern — state 'Exact match', 'Near match', or 'No close match' + the archetype name. Add a 2–3 sentence, practitioner-friendly explanation of the archetype referencing user evidence: Why this match (and where it differs) — using bullets for both and differences/misfits. Ensure that the differential analysis is consisten with the four archetypes.\n,
            D) Recommendations: 2-3 actionable steps for the next 90 days. Keep them tightly tied to the archetype’s mechanism.\n,
            If inputs are insufficient to proceed, output only: 'Please try the canvas again.'""")},
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
 
        st.subheader(translations["step1_description"][language])
        elica1 = st.text_area(translations["share_innovation1"][language], key='elica1')
        st.subheader(translations["step2_description"][language])
        elica2 = st.text_area(translations["share_innovation2"][language], key='elica2')
        st.subheader(translations["step3_description"][language])
        elica3 = st.text_area(translations["share_innovation3"][language], key='elica3')
        st.subheader(translations["step4_description"][language])
        elica4 = st.text_area(translations["share_innovation4"][language], key='elica4')
        st.subheader(translations["step5_description"][language])
        elica5 = st.text_area(translations["share_innovation5"][language], key='elica5')
        st.subheader(translations["step6_description"][language])
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
