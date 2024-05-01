# streamlit_helper_fun.py
import streamlit as st
from datetime import datetime
from st_ui_constants import (USER_MESSAGE_CLASS, BOT_MESSAGE_CLASS,
                             MESSAGE_DISPLAY_COLUMNS, MESSAGE_GAP,
                             CHAT_HISTORY_EXPANDED, BOLD_TAG, ITALIC_TAG,
                             BLOCKQUOTE_TAG, DEFAULT_LANGUAGE)
from app_constants import LAST_N_MESSAGES, TIMESTAMP_FORMAT


class MessageDisplay:
    @staticmethod
    def display_code_snippet(code_content):
        st.code(code_content, language=DEFAULT_LANGUAGE)

    @staticmethod
    def display_image(image_url):
        st.image(image_url)

    @staticmethod
    def display_link(url):
        st.markdown(f"<a href='{url}' target='_blank'>{url}</a>", unsafe_allow_html=True)

    @staticmethod
    def display_formatted_text(message_content):
        if message_content.startswith('**'):
            tag = BOLD_TAG
        elif message_content.startswith('*'):
            tag = ITALIC_TAG
        elif message_content.startswith('>'):
            tag = BLOCKQUOTE_TAG
        else:
            return None
        formatted_text = message_content.strip('*>**')
        st.markdown(f"<{tag}>{formatted_text}</{tag}>", unsafe_allow_html=True)
        return True

    @staticmethod
    def display_regular_message(message_class, message_content, timestamp):
        st.markdown(f"<div class='{message_class}'>{message_content}<div class='message-timestamp'>{timestamp}</div></div>", unsafe_allow_html=True)

    @staticmethod
    def display_determined_message(message_class, message_content, timestamp):
        if message_content.startswith('```'):
            MessageDisplay.display_code_snippet(message_content.strip('```'))
        elif message_content.startswith('![]('):
            MessageDisplay.display_image(message_content.strip('![]()'))
        elif message_content.startswith('http'):
            MessageDisplay.display_link(message_content)
        elif message_content.startswith(('**', '*', '>')):
            if not MessageDisplay.display_formatted_text(message_content):
                MessageDisplay.display_regular_message(message_class, message_content, timestamp)
        else:
            MessageDisplay.display_regular_message(message_class, message_content, timestamp)

    @staticmethod
    def convert_timestamp(utc_timestamp):
        return datetime.fromisoformat(utc_timestamp).astimezone().strftime(TIMESTAMP_FORMAT)

    @staticmethod
    def determine_message_class(role):
        return USER_MESSAGE_CLASS if role == 'user' else BOT_MESSAGE_CLASS

    @staticmethod
    def setup_message_layout(message_class):
        if message_class == USER_MESSAGE_CLASS:
            col_message, col_empty = st.columns([3, 1], gap="medium")
        else:
            col_empty, col_message = st.columns([1, 3], gap="medium")
        return col_message, col_empty

    @staticmethod
    def display_messages(messages):
        # messages_to_display = messages[-LAST_N_MESSAGES:]

        with st.container():
            with st.expander("Chat History", expanded=CHAT_HISTORY_EXPANDED):
                i = 0
                for msg in reversed(messages):
                    # timestamp = MessageDisplay.convert_timestamp(msg[1])
                    # Get the current timestamp
                    timestamp_now = datetime.now().isoformat()

                    # Convert the timestamp to a string
                    timestamp = MessageDisplay.convert_timestamp(timestamp_now)
                    if i % 2 == 0:
                        message_class = MessageDisplay.determine_message_class("user")
                    else:
                        message_class = MessageDisplay.determine_message_class("ai")
                    message_content = msg.content
                    i = i + 1
                    col_message, col_empty = MessageDisplay.setup_message_layout(message_class)

                    with col_message:
                        MessageDisplay.display_determined_message(message_class, message_content,
                                                                  timestamp)

                    with col_empty:
                        st.empty()

    @staticmethod
    def initialize_session_states():
        if 'user_input' not in st.session_state:
            st.session_state['user_input'] = ""

    @staticmethod
    def setup_page_config():
        st.set_page_config(layout="wide")

    @staticmethod
    def display_user_and_ai_messages(st_message_display, user_input, ai_response):
        # For user input
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message_class = USER_MESSAGE_CLASS
        message_content = user_input
        col_message, col_empty = st_message_display.setup_message_layout(message_class)
        with col_message:
            st_message_display.display_determined_message(message_class, message_content,
                                                          timestamp)

        # For AI response
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message_class = BOT_MESSAGE_CLASS
        message_content = ai_response
        col_message, col_empty = st_message_display.setup_message_layout(message_class)
        with col_message:
            st_message_display.display_determined_message(message_class, message_content,
                                                          timestamp)