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

# IMPORTANT: Handle query parameters at the very top before any UI renders
if "device_id" not in st.query_params:
    st.query_params["device_id"] = str(uuid.uuid4())

device_id = st.query_params["device_id"]
if isinstance(device_id, list):
    device_id = device_id[0]

st.title("💖 CRUSH MATCHER 💖")
st.markdown("---")

# Privacy Notice
st.info("🔒 **PRIVACY NOTICE:** This program is completely anonymous. The admin cannot see who your crush is or track your identity. Type freely! 🕵️‍♂️✨")

data = load_data()

# Check if this specific device/browser already registered a name
registered_name = data["device_names"].get(device_id)
user_name = None

if registered_name:
    st.success(f"Welcome back! Your identity on this device is locked as: **{registered_name.title()}**")
    user_name = registered_name
else:
    st.subheader("👋 Welcome!")
    st.write("Enter your real name. **Note:** Once locked, this device can only use this name to prevent trolling or impersonation.")
    
    name_input = st.text_input("What's your name?").strip().lower()
    
    if st.button("Lock In Name"):
        if not name_input:
            st.error("Name cannot be empty.")
        else:
            # Check if this name is already taken by ANOTHER device
            name_already_taken = False
            for dev, name in data["device_names"].items():
                if name == name_input and dev != device_id:
                    name_already_taken = True
                    break
            
            if name_already_taken:
                st.error("This name is already registered on another device! You cannot impersonate someone else.")
            else:
                # Permanently bind this name to this device ID
                data["device_names"][device_id] = name_input
                save_data(data)
                st.success(f"Success! Name locked to this device: {name_input.title()}")
                st.rerun()

# If user's name is locked in, show crush input
if user_name:
    st.markdown("---")
    crush_input = st.text_input("What's the name of your crush?").strip().lower()
    
    if st.button("Submit Crush"):
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
