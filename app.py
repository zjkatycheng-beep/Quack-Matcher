import json
import os
import uuid
import streamlit as st

DATA_FILE = "crush_data.json"

def load_data():
    """Loads existing submissions and account data safely."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if "accounts" not in data: data["accounts"] = {}
                if "device_accounts" not in data: data["device_accounts"] = {}
                if "submissions" not in data: data["submissions"] = []
                return data
        except json.JSONDecodeError:
            pass
    return {"accounts": {}, "device_accounts": {}, "submissions": []}

def save_data(data):
    """Saves data back to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Page Configuration
st.set_page_config(page_title="Crush Matcher", page_icon="💖")

# Handle persistent device ID via query parameters safely
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

# Initialize session state for login
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

user_name = st.session_state.logged_in_user

# If not logged in in session state
if not user_name:
    bound_user = data["device_accounts"].get(device_id)
    
    if bound_user:
        # Recognized device: Prompt for PIN to unlock
        st.subheader(f"Welcome back, {bound_user.title()}! 💕")
        pin_input = st.text_input("Enter your 4-digit PIN to unlock:", type="password").strip()
        
        if st.button("Unlock Account"):
            if pin_input == data["accounts"].get(bound_user, {}).get("pin"):
                st.session_state.logged_in_user = bound_user
                st.rerun()
            else:
                st.error("Incorrect PIN! Please try again.")
    else:
        # Check if this device already created an account previously (even if device_accounts missed it)
        # We can check via a secondary safeguard or restrict the creation tab entirely
        st.subheader("👋 Welcome to Crush Matcher!")
        st.write("*Note: Each device is restricted to creating only **one** account to prevent trolling.*")
        
        tab1, tab2 = st.tabs(["Create Account", "Log In Existing Account"])
        
        with tab1:
            # Check if this device already has an account associated in storage
            device_already_has_account = False
            for d, u in data["device_accounts"].items():
                if d == device_id:
                    device_already_has_account = True
                    break
            
            if device_already_has_account:
                st.error("❌ This device has already created an account! You cannot create another one. Please use the 'Log In' tab if you have an existing account.")
            else:
                with st.form("create_form"):
                    new_name = st.text_input("Choose your name:").strip().lower()
                    new_pin = st.text_input("Choose a 4-digit PIN:", type="password").strip()
                    create_submitted = st.form_submit_button("Create Account")
                    
                    if create_submitted:
                        if not new_name or not new_pin:
                            st.error("Name and PIN cannot be empty.")
                        elif len(new_pin) < 4:
                            st.error("PIN must be at least 4 digits.")
                        elif new_name in data["accounts"]:
                            st.error("This name is already taken! Please choose a different name or log in.")
                        else:
                            # Register account and permanently lock this device ID
                            data["accounts"][new_name] = {"pin": new_pin}
                            data["device_accounts"][device_id] = new_name
                            save_data(data)
                            st.session_state.logged_in_user = new_name
                            st.success("Account created successfully!")
                            st.rerun()
        
        with tab2:
            with st.form("login_form"):
                login_name = st.text_input("Your name:").strip().lower()
                login_pin = st.text_input("Your 4-digit PIN:", type="password").strip()
                login_submitted = st.form_submit_button("Log In")
                
                if login_submitted:
                    if not login_name or not login_pin:
                        st.error("Name and PIN cannot be empty.")
                    elif login_name not in data["accounts"]:
                        st.error("Account not found.")
                    elif data["accounts"][login_name]["pin"] != login_pin:
                        st.error("Incorrect PIN.")
                    else:
                        # Bind this device to the logged-in account
                        data["device_accounts"][device_id] = login_name
                        save_data(data)
                        st.session_state.logged_in_user = login_name
                        st.success("Logged in successfully!")
                        st.rerun()

# If logged in, show crush submission screen
if st.session_state.logged_in_user:
    user_name = st.session_state.logged_in_user
    st.success(f"Logged in as: **{user_name.title()}**")
    
    if st.button("Log Out"):
        st.session_state.logged_in_user = None
        st.rerun()
        
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
