#############################################
# Streamlit UI operation. #
#############################################
# from io import BytesIO
import io
from datetime import datetime, timezone
import json
import base64

import logging
import boto3
from botocore.exceptions import ClientError
import streamlit as st
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from llm_qa_experiment import LLMRagQA
from streamlit_sidebar import initialize_sidebar, clear_chat_history, \
    on_project_type_change, on_project_change
from streamlit_app_style import css_style
from chat_history_sql_db import ChatHistoryDB, AIMessageDB, HumanMessageDB
from streamlit_helper_fun import MessageDisplay
from llm_experiment3 import LLMChatbot, NOVEL_PROMPT
import jsonpickle

bucket_name = 'streamlit-pdf-test'

# Initialize AWS S3 client
session = boto3.Session()
s3 = session.client('s3', region_name='us-east-1')

# Initialize Boto3 client for Lambda
lambda_client = boto3.client('lambda')

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")

# Upload the file to S3
def upload_to_s3(file_content, bucket, object_name):
    try:
        # Convert bytes to base64 string before serialization
        file_content_base64 = base64.b64encode(file_content).decode('utf-8')
        
        lambda_client.invoke(
            FunctionName='upload-pdf-to-s3',
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'file': {
                    'content': file_content_base64,
                    'name': object_name
                },
                'bucket': bucket
            })
        )
        print('File Successfully Uploaded')
    except ClientError as e:
        logging.error(e)
        return False
    return True


st.set_page_config(layout="centered")
st.markdown(css_style, unsafe_allow_html=True)

# Function to submit user input and get a response
def handle_submit(user_input, ll_response):

    # Get LLM response (placeholder)
    ai_response = ll_response

    # Convert any text like json to a string or a list of strings
    if isinstance(ai_response, dict):
        ai_response = str(ai_response)
    elif isinstance(ai_response, list):
        ai_response = '\n'.join(ai_response)
    else:
        ai_response = str(ai_response)

    response = lambda_client.invoke(
                FunctionName='dynamodb_history',
                InvocationType='RequestResponse',
                Payload=json.dumps({
                    'table_name': 'SessionTable',
                    'session_id': "0",
                    'user_input': user_input,
                    'ai_response': ai_response 
                })
            )    
    history_message  = jsonpickle.decode(json.loads(response['Payload'].read())['body'])
    
    # Update chat history in session state
    st.session_state['chat_history_text'] = update_chat_history(history_message)

    # Clear the input field by rerunning the app which will reset the session state
    # st.rerun()


# Function to update chat history from the database
def update_chat_history(all_messages):
    timestamp = datetime.now().isoformat()
    HumanMessage = "user"
    AIMessage = "ai"
    if all_messages:
        chat_history = "\n".join(f"{timestamp} {HumanMessage}: {all_messages[0].content}")
        chat_history += "\n".join(f"{timestamp} {AIMessage}: {all_messages[1].content}")
    else:
        # Handle the case when the list is empty
        chat_history = "No messages available."
    return chat_history


# Function to get number of last messages from the database to send to LLM
# def get_last_messages(db_con, num_messages):
#     all_messages = db_con.get_all_messages()
#     last_messages = "\n".join(f"{msg[3]}" for msg in all_messages[-num_messages:])
#     return last_messages


# Main function to render the app
def main():
    st.subheader('Feature/Scenario Generator')
    # Initialize session state variables if they don't exist
    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = ""
    if 'chat_history_text' not in st.session_state:
        st.session_state['chat_history_text'] = ""
    if 'scenarios' not in st.session_state:
        st.session_state.scenarios = []
    # Add response to the session state
    if 'response' not in st.session_state:
        st.session_state.response = []

    # Check if the table exists
    table_name = "SessionTable"
    try:
        dynamodb.Table(table_name).table_status
        print(f"Table {table_name} already exists.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Table {table_name} does not exist. Creating...")

        # Create the DynamoDB table.
        table = dynamodb.create_table(
            TableName="SessionTable",
            KeySchema=[{"AttributeName": "SessionId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "SessionId", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        # Wait until the table exists.
        table.meta.client.get_waiter("table_exists").wait(TableName="SessionTable")
        print(f"Table {table_name} created successfully.")

    response = lambda_client.invoke(
                FunctionName='dynamodb_history',
                InvocationType='RequestResponse',
                Payload=json.dumps({
                    'table_name': table_name,
                    'session_id': "0",
                    'user_input': "",
                    'ai_response': "" 
                })
            )
    # history = DynamoDBChatMessageHistory(table_name=table_name, session_id="0")

    history_message  = jsonpickle.decode(json.loads(response['Payload'].read())['body'])
    # print("Response:", history_message)
    # print("hostory: ", history.messages)

    # Initialize sidebar with project and scenario dropdowns
    page_selection = initialize_sidebar()
    project_type = on_project_type_change()
    project_name = on_project_change()
    st.write(f"You selected project type: {project_type} and project name: {project_name}")
    clear_chat_history(dynamodb, table_name)

    # Upload the file:
    uploaded_files = st.file_uploader(
        label="Upload PDF files", type=["pdf"], accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Trigger S3 upload function
            file_content = uploaded_file.getvalue()
            upload_to_s3(file_content, bucket_name, uploaded_file.name)
            st.write(f"Uploaded {uploaded_file.name} to S3")


    # Main content area for chat interaction
    with st.form('chat_form1', clear_on_submit=True):
        # Text area for user input
        user_input = st.text_area("Ask your Feature question here...", height=200)
        if user_input:
            print("You entered:", user_input)
        # Submit button for the form
        submitted = st.form_submit_button('Send')
        # Display past messages, assuming MessageDisplay is a defined class
        st_disp = MessageDisplay()
        st_disp.display_messages(history_message)
        
    response = {'output': ""}
    if submitted:
        if project_type is None or project_name is None:
            st.error("Please select a project type and project name.")
            return
        if not uploaded_files:
            st.warning("Please upload PDF documents to continue.")
            st.stop()
            return
        llm_rag_qa = LLMRagQA()
        # uploaded_file get the file path
        query_rag = llm_rag_qa.load_agent(uploaded_files=uploaded_files, bucket_name=bucket_name)
        query_refine = query_rag.invoke({"query": user_input})
        output_question = query_refine['result']
        st.markdown(f"**Your Query:** `{user_input}`")
        st.markdown("### Refined Query:")
        st.code(f"{output_question}", language="python")
        st.markdown(
            """
            ### Solution Compilation
            The response is being compiled based on the Agent's analysis. Please note that response times may vary and accuracy can be influenced by the specificity of your query. For improved results, consider providing more detailed information.
            """
        )
        with st.spinner('Processing...'):
            st.session_state.response = []
            # Initialize the chatbot instance
            chatbot = LLMChatbot()
            # Format the user input with the provided prompt template
            user_input_prompt = NOVEL_PROMPT.format(research_question=user_input)

            # Generate the chatbot response
            try:
                response = chatbot.run_agent(user_input_prompt, chat_history=None)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                # st.stop()
                return
            # Add response to the session state
            if isinstance(response, dict) and response.get('output', '') != "":
                print("Response Output:", response['output'])
                final_response = response['output']
                if isinstance(final_response, dict):
                    final_response = final_response.get('feature_file', '')
                else:
                    final_response = response['output']

                st.session_state.response.append(final_response)

            # Update the chat history in the session state
            st.session_state.chat_history_text += format_chat_update(user_input,
                                                                     final_response)

            # Handle the submission by storing it in the database
            handle_submit(user_input, final_response)

    # Check if the response has been set and is not empty
    if len(st.session_state.response) > 0:
        # Display the feature file title
        st.subheader("Main Feature Feature File:")
        if 'scenarios' in st.session_state:
            st.session_state.scenarios = []
        # Display the formatted feature file
        response_output = st.session_state.response[0]
        st.code(response_output)
        # Create a download link for the feature file
        get_text_download_link(response_output, 'feature_file')


def format_chat_history(concatenated_messages):
    """Formats the chat history into HumanMessage and AIMessage objects."""
    messages = concatenated_messages.split('\n')
    formatted_history = []

    for i, message in enumerate(messages):
        if i % 2 == 0:
            formatted_history.append(HumanMessage(content=message))
        else:
            formatted_history.append(AIMessage(content=message))

    return formatted_history


def format_chat_update(user_input, bot_response):
    """Formats the chat update for session state."""
    return f"**You:** {user_input}\n**LLM:** {bot_response}\n\n"


def format_scenario_as_markdown(scenario):
    # Format steps with a newline character after each step
    steps_formatted = '\n'.join(
        f"  * {step}" for step in scenario.steps)  # Add two spaces for indentation
    scenario_text = f"Feature: {scenario.feature}\n\n" \
                    f"@{scenario.tag}\n\n" \
                    f"Scenario: {scenario.scenario_name} \n" \
                    f"{steps_formatted}"
    return scenario_text


def get_text_download_link(feature_text, key):
    """Generates a link allowing the data in a given panda dataframe to be downloaded in: csv, json, and xlsx formats."""

    # Make sure to check feature_text is not empty and is a string
    if not isinstance(feature_text, str) or feature_text == "":
        return
    buffer = io.BytesIO(feature_text.encode('utf-8'))
    st.download_button(
        label="Download Feature File",
        data=buffer,
        file_name="feature_file.txt",
        mime='text/plain',
        key=f"download_{key}"
    )


# main function
if __name__ == "__main__":
    main()
