import json
import os
import uuid
import streamlit as st

DATA_FILE = "crush_data.json"

def load_data():
    """Loads existing submissions and device bindings from the JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"device_names": {}, "submissions": []}
    return {"device_names": {}, "submissions": []}

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

# Safely handle URL parameters for different Streamlit versions to persist device ID
try:
    if "device_id" not in st.query_params:
        st.query_params["device_id"] = str(uuid.uuid4())
    device_id = st.query_params["device_id"]
    if isinstance(device_id, list):
        device_id = device_id[0]
except AttributeError:
    # Fallback for older Streamlit versions if needed
    query_params = st.experimental_get_query_params()
    if "device_id" not in query_params:
        device_id = str(uuid.uuid4())
        st.experimental_set_query_params(device_id=device_id)
    else:
        device_id = query_params["device_id"][0]

# Check if this device already registered a name in the database
registered_name = data["device_names"].get(device_id)
user_name = None

if registered_name:
    st.success(f"Welcome back! Your name on this device is locked in as: **{registered_name.title()}**")
    user_name = registered_name
else:
    with st.form("name_form"):
        name_input = st.text_input("What's your name?").strip().lower()
        submitted = st.form_submit_button("Lock In Name")
        if submitted:
            if name_input:
                data["device_names"][device_id] = name_input
                save_data(data)
                st.success(f"Success! Name locked for this device: {name_input.title()}")
                st.rerun()
            else:
                st.error("Name cannot be empty.")

# If user's name is locked in, show crush input
if user_name:
    st.markdown("---")
    with st.form("crush_form"):
        crush_input = st.text_input("What's the name of your crush?").strip().lower()
        crush_submitted = st.form_submit_button("Submit Crush")
        
        if crush_submitted:
            if not crush_input:
                st.error("Crush name cannot be empty.")
            elif user_name == crush_input:
                st.warning("Nice try! You can't crush on yourself. 😉")
            else:
                new_sub = {"user": user_name, "crush": crush_input}
                
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
                        if sub["user"] == crush_input and sub["crush"] == user_name:
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
