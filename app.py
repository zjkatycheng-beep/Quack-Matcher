import json
import os
import streamlit as st

DATA_FILE = "crush_data.json"

def load_data():
    """Loads existing submissions from the JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"submissions": []}
    return {"submissions": []}

def save_data(data):
    """Saves data back to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Page Configuration
st.set_page_config(page_title="Crush Matcher", page_icon="💖")

st.title("💖 CRUSH MATCHER 💖")
st.markdown("---")

# Privacy Notice
st.info("🔒 **PRIVACY NOTICE:** This program is completely anonymous. The admin cannot see who your crush is or track your identity. Type freely! 🕵️‍♂️✨")

data = load_data()

# Initialize session state to lock the user's name for this browser session
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# Step 1: Get User's Name
if not st.session_state.user_name:
    name_input = st.text_input("What's your name?").strip().lower()
    if st.button("Lock In Name"):
        if name_input:
            st.session_state.user_name = name_input
            st.rerun()
        else:
            st.error("Name cannot be empty.")
else:
    # Step 2: User is locked in, show crush input
    st.success(f"Your name is locked in as: **{st.session_state.user_name.title()}**")
    
    crush_input = st.text_input("What's the name of your crush?").strip().lower()
    
    if st.button("Submit Crush"):
        if not crush_input:
            st.error("Crush name cannot be empty.")
        elif st.session_state.user_name == crush_input:
            st.warning("Nice try! You can't crush on yourself. 😉")
        else:
            new_sub = {"user": st.session_state.user_name, "crush": crush_input}
            
            # Prevent duplicate identical submissions
            if new_sub in data["submissions"]:
                st.warning("You've already entered this crush before!")
            else:
                data["submissions"].append(new_sub)
                save_data(data)
                
                # Check match status logic
                is_match = False
                crush_has_used_program = False
                
                for sub in data["submissions"]:
                    if sub["user"] == crush_input:
                        crush_has_used_program = True
                    if sub["user"] == crush_input and sub["crush"] == st.session_state.user_name:
                        is_match = True
                        break
                
                st.markdown("---")
                if is_match:
                    st.balloons()
                    st.success("CONGRATS!!! You're a MATCHHHHHH (go confess) 🎉🔥❤️")
                elif not crush_has_used_program:
                    st.info("Your crush hasn't used this program yet. Fingers crossed they type your name too... 🤫✨")
                else:
                    st.error("Sorry. Not a match :(. 💔")
