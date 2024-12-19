import streamlit as st

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Function to toggle the theme
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Add a button to toggle the theme
st.button('Switch Theme', on_click=toggle_theme)

# Apply the theme styles
if st.session_state.theme == 'dark':
    st.markdown(
        """
        <style>
        /* Change the background of the entire page */
        .css-18e3th9 {
            background-color: black !important;
        }

        /* Change the color of all text on the page */
        .css-1d391kg, .css-18e3th9, .stTextInput, .stTextArea, .stButton {
            color: white !important;
        }

        /* Change the background color of text inputs */
        .stTextInput>div>div>input, 
        .stTextArea>div>div>textarea {
            background-color: #333333 !important;
            color: white !important;
        }

        /* Change the button color */
        .stButton button {
            background-color: #444444 !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        /* Change the background of the entire page */
        .css-18e3th9 {
            background-color: white !important;
        }

        /* Change the color of all text on the page */
        .css-1d391kg, .css-18e3th9, .stTextInput, .stTextArea, .stButton {
            color: black !important;
        }

        /* Change the background color of text inputs */
        .stTextInput>div>div>input, 
        .stTextArea>div>div>textarea {
            background-color: white !important;
            color: black !important;
        }

        /* Change the button color */
        .stButton button {
            background-color: #007bff !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Page content
st.header("Streamlit Dark and Light Mode Switcher")
st.write(f"**Current Theme: {st.session_state.theme.capitalize()}**")
st.text_input("Enter some text")
st.text_area("Write a message")
