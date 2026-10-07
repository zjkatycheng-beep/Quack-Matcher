import json
import os
import uuid
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

DATA_FILE = "crush_data.json"

# Initialize Cookies Manager (change prefix/password to anything secure)
cookies = EncryptedCookieManager(prefix="crush_matcher_app", password="random-secure-password-string")

if not cookies.ready():
    st.stop()  # Wait for cookies to load

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

# Check if a device ID cookie already exists, otherwise create one
if "device_id" not in cookies:
    cookies["device_id"] = str(uuid.uuid4())
    cookies.save()

device_id = cookies["device_id"]

# Check if this device already registered a name in the database
registered_name = data["device_names"].get(device_id)

user_name = None

if registered_name:
    st.success(f"Welcome back! Your name on this device is locked in as: **{registered_name.title()}**")
    user_name = registered_name
else:
    name_input = st.text_input("What's your name?").strip().lower()
    if st.button("Lock In Name"):
        if name_input:
            # Save the binding to JSON
            data["device_names"][device_id] = name_input
            save_data(data)
            st.success(f"Success! Name locked for this device: {name_input.title()}")
            st.rerun()
        else:
            st.error("Name cannot be empty.")

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
