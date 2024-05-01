# streamlit_app_style.py

css_style = """
<style>
.streamlit-expanderHeader {
    font-size: large;
    font-weight: bold;
    color: #2E3B55; /* Professional dark blue */
    margin-bottom: 5px;
}

/* Adjusting message bubbles */
.user-message, .bot-message {
    max-width: 100%; /* Prevents the text from stretching too long */
    padding: 12px 18px;
    border-radius: 16px;
    margin-bottom: 20px; /* Increase spacing between messages */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    font-size: 0.9rem;
    word-wrap: break-word; /* Un-comment this line to ensure text wraps */
}

.user-message {
    align-self: flex-end;
    background-color: #4A90E2; /* Pleasant user-message color */
    color: white;
}

.bot-message {
    align-self: flex-start;
    background-color: #F5F5F5; /* Light background for bot messages */
    color: #4A4A4A; /* Darker text for contrast */
}

.message-timestamp {
    align-self: flex-end;
    font-size: 0.75rem;
    color: #939FA5; /* Subdued color for timestamp */
    margin-top: 1px;
}

/* Additional styles */
.code-block {
    background-color: #F7F7F7; /* Light background for code blocks */
    border-left: 4px solid #4A90E2; /* Blue left border for code blocks */
    padding: 10px;
    font-family: 'Courier New', Courier, monospace;
    margin: 10px 0;
    overflow-x: auto; /* Allows horizontal scrolling for long lines of code */
}

.error-message {
    color: #D9534F; /* Error color */
    background-color: #FFD2D2; /* Light red background for errors */
    padding: 10px;
    border-radius: 8px; /* Rounded corners for error messages */
    margin: 10px 0;
    text-align: left;
}

.interactive-button {
    background-color: #4A90E2; /* Consistent with user-message color */
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.interactive-button:hover {
    background-color: #357ABD; /* Darker shade on hover */
}

/* Layout and container styles */
.container {
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

/* Style adjustments for a more professional look */
.stTextInput, .stTextArea {
    border: 1px solid #CED4DA; /* Subtle borders for input fields */
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 10px;
}

.stButton>button {
    width: 100%;
    padding: 10px;
    border-radius: 4px;
    border: none;
    background-color: #4A90E2;
    color: white;
}

.stButton>button:hover {
    background-color: #357ABD;
}

/* Centering the main content area */
#main {
    margin-left: auto;
    margin-right: auto;
    max-width: 800px; /* Adjust the width as needed */
}

/* Enlarge chat space - this targets the container of the expander content */
.stExpander {
    width: 100%;
}

/* Additional container styling for chat history to give it more space */
.chat-history-container {
    padding: 10px 20px;
    background-color: #fff; /* Or any other color */
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

div.stButton > button:first-child {{ 
            background-color: #0d6efd; 
            color: white;
            border-radius: 5px 5px 5px 5px;
            border: none;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
            box-shadow: 0 9px #999;
        }}
        
div.stButton > button:first-child:hover {{ 
    background-color: #0056b3;
    box-shadow: 0 5px #666;
    transform: translateY(4px);
}}

div.download_button > button:first-child {{
    background-color: #0d6efd; 
    color: white;
    border-radius: 5px 5px 5px 5px;
    border: none;
    padding: 10px 24px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    transition-duration: 0.4s;
    cursor: pointer;
    box-shadow: 0 9px #999;
}}

</style>
"""