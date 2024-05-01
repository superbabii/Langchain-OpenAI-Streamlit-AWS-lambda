# streamlit_sidebar.py
import streamlit as st

from app_constants import PROJECT_TYPE_OPTIONS, PROJECT_NAMES_OPTIONS


def initialize_sidebar():
    st.sidebar.subheader("Welcome to the Main Feature Scenario Generator!")

    # Initialize the project name and project type in session state
    if 'project_name' not in st.session_state:
        st.session_state['project_name'] = None
    if 'project_type' not in st.session_state:
        st.session_state['project_type'] = None


def on_project_change():
    st.sidebar.write("Select a project:")
    project_options = PROJECT_NAMES_OPTIONS
    selection = st.sidebar.selectbox(label='Select Project', options=project_options,
                                     key='project_name',
                                     label_visibility='collapsed',
                                     placeholder='Select a project',
                                     index=None)
    return selection


def on_project_type_change():
    st.sidebar.write("Select a project type:")
    project_type_options = PROJECT_TYPE_OPTIONS
    selection = st.sidebar.selectbox(label='Project Type:', options=project_type_options,
                                     key='project_type',
                                     label_visibility='collapsed',
                                     placeholder='Select a project type',
                                     index=None)
    return selection


def get_project_type():
    # Return the project type from session state and check if it is None
    if 'project_type' in st.session_state and st.session_state['project_type'] is not None:
        return st.session_state['project_type']
    else:
        return None


def get_project_name():
    # Return the project name from session state and check if it is None
    if 'project_name' in st.session_state and st.session_state['project_name'] is not None:
        return st.session_state['project_name']
    else:
        return None


def handle_page_navigation(pages):
    # Function to handle page navigation
    page = st.sidebar.selectbox("Choose a page:", tuple(pages.keys()))
    pages[page]()
    return page


def clear_chat_history(dynamodb, table_name):
    # Add empty space to push the button to the bottom
    for _ in range(34):
        st.sidebar.write("")
    clear_chat = st.sidebar.button("Clear chat history")
    if clear_chat:
        table = dynamodb.Table(table_name)
        response = table.scan()
        for item in response['Items']:
            table.delete_item(
                Key={
                    'SessionId': item['SessionId']
                }
            )
        st.sidebar.success("Chat history cleared successfully.")
        st.rerun()
