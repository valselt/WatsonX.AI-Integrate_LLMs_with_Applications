"""
author: Elena Lowery

This code sample shows how to invoke Large Language Models (LLMs) deployed in watsonx.ai.
Documentation: # https://ibm.github.io/watson-machine-learning-sdk/foundation_models.html#
You will need to provide your IBM Cloud API key and a watonx.ai project id (any project)
for accessing watsonx.ai
This example shows a simple generation or Q&A use case without comprehensive prompt tuning
"""

# Install the wml and streamlit api your Python env prior to running this example:
# pip install ibm-watson-machine-learning
# pip install streamlit

# In non-Anaconda Python environments, you may also need to install dotenv
# pip install python-dotenv

# For reading credentials from the .env file
import os
from dotenv import load_dotenv

import streamlit as st

from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes, DecodingMethods

# Important: hardcoding the API key in Python code is not a best practice. We are using
# this approach for the ease of demo setup. In a production application these variables
# can be stored in an .env or a properties file

# URL of the hosted LLMs is hardcoded because at this time all LLMs share the same endpoint
url = "https://us-south.ml.cloud.ibm.com"

# These global variables will be updated in get_credentials() functions
watsonx_project_id = ""
# Replace with your IBM Cloud key
api_key = ""

def get_credentials():

    load_dotenv()

    # Update the global variables that will be used for authentication in another function
    globals()["api_key"] = os.getenv("api_key", None)
    globals()["watsonx_project_id"] = os.getenv("project_id", None)

    print("*** Got credentials***")

# The get_model function creates an LLM model object with the specified parameters
def get_model(model_type,max_tokens,min_tokens,decoding,stop_sequences):

    generate_params = {
        GenParams.MAX_NEW_TOKENS: max_tokens,
        GenParams.MIN_NEW_TOKENS: min_tokens,
        GenParams.DECODING_METHOD: decoding,
        GenParams.STOP_SEQUENCES:stop_sequences
    }

    model = Model(
        model_id=model_type,
        params=generate_params,
        credentials={
            "apikey": api_key,
            "url": url
        },
        project_id=watsonx_project_id
        )

    return model

def get_prompt(question):

    # Prompts are passed to LLMs as one string. We are building it out as separate strings for ease of understanding
    # Instruction
    instruction = "Answer this question briefly."
    # Examples to help the model set the context
    examples = "\n\nQuestion: What is the capital of Germany\nAnswer: Berlin\n\nQuestion: What year was George Washington born?\nAnswer: 1732\n\nQuestion: What are the main micro nutrients in food?\nAnswer: Protein, carbohydrates, and fat\n\nQuestion: What language is spoken in Brazil?\nAnswer: Portuguese \n\nQuestion: "
    # Question entered in the UI
    your_prompt = question
    # Since LLMs want to "complete a document", we're are giving it a "pattern to complete" - provide the answer
    end_prompt = "Answer:"

    final_prompt = instruction + examples + your_prompt + end_prompt

    return final_prompt

def answer_questions():

    # Set the api key and project id global variables
    get_credentials()

    # Web app UI - title and input box for the question
    st.title('🌠Watsonx.ai LLM')
    user_question = st.text_input('Ask a question, for example: What is Indonesia?', key="input_text", label_visibility="visible")

    # Full-width buttons below the text input
    col1, col2 = st.columns([0.5, 0.5])  # Split equally

    with col1:
        send_button = st.button("Send", use_container_width=True)
    with col2:
        clear_button = st.button("Clear Input", use_container_width=True)

    # Logic for the buttons
    if clear_button:
        st.session_state["input_text"] = ""  # Clear the input text

    if send_button:
        # Prevent empty questions
        if len(user_question.strip()) == 0:
            user_question = "What is Indonesia?"

        # Get the prompt
        final_prompt = get_prompt(user_question)

        # Display our complete prompt - for debugging/understanding
        print(final_prompt)

        # Model parameters
        model_type = ModelTypes.FLAN_UL2
        max_tokens = 100
        min_tokens = 20
        decoding = DecodingMethods.GREEDY
        stop_sequences = ['.']

        # Get the model
        model = get_model(model_type, max_tokens, min_tokens, decoding, stop_sequences)

        # Generate response
        generated_response = model.generate(prompt=final_prompt)
        model_output = generated_response['results'][0]['generated_text']

        # Display output on the Web page
        st.markdown(f"""
            **Answer to your question:** {user_question} \
            *{model_output}*
        """, unsafe_allow_html=True)

        # Display the model type
        st.markdown(f"**Model Used:** {model_type.value if hasattr(model_type, 'value') else model_type}")
        
# Invoke the main function
answer_questions()
