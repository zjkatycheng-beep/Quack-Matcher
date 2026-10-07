import json
import os
import uuid

DATA_FILE = "crush_data.json"
DEVICE_FILE = "device_token.txt"

def get_device_id():
    """Gets or creates a unique ID for this device/installation."""
    if os.path.exists(DEVICE_FILE):
        with open(DEVICE_FILE, "r") as f:
            return f.read().strip()
    else:
        device_id = str(uuid.uuid4())
        with open(DEVICE_FILE, "w") as f:
            f.write(device_id)
        return device_id

def load_data():
    """Loads existing submissions and device bindings from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"device_names": {}, "submissions": []}

def save_data(data):
    """Saves data back to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def main():
    device_id = get_device_id()
    data = load_data()
    
    print("========================================")
    print("          💖 CRUSH MATCHER 💖           ")
    print("========================================")
    print("🔒 PRIVACY NOTICE:")
    print("This program is completely anonymous.")
    print("The admin cannot see who your crush is or")
    print("track your identity. Type freely! 🕵️‍♂️✨\n")
    
    # Check if this device already registered a name
    registered_name = data["device_names"].get(device_id)
    
    if registered_name:
        print(f"Welcome back! Your name on this device is locked as: **{registered_name.title()}**")
        user_name = registered_name
    else:
        user_name = input("What's your name? ").strip().lower()
        if not user_name:
            print("Error: Name cannot be empty.")
            return
        # Lock this name to this device
        data["device_names"][device_id] = user_name
        save_data(data)
        print(f"Success! Name locked for this device: {user_name.title()}\n")

    crush_name = input("What's the name of your crush? ").strip().lower()
    if not crush_name:
        print("Error: Crush name cannot be empty.")
        return

    # Prevent crushing on oneself
    if user_name == crush_name:
        print("\nNice try! You can't crush on yourself. 😉")
        return

    # Check if this exact submission already exists
    new_sub = {"user": user_name, "crush": crush_name}
    if new_sub in data["submissions"]:
        print("\nYou've already entered this crush before!")
        return

    # Save the new submission
    data["submissions"].append(new_sub)
    save_data(data)

    # Check match status logic
    is_match = False
    crush_has_used_program = False

    for sub in data["submissions"]:
        # Check if crush has entered *anyone* into the system
        if sub["user"] == crush_name:
            crush_has_used_program = True
        
        # Check if it's a mutual match
        if sub["user"] == crush_name and sub["crush"] == user_name:
            is_match = True
            break

    print("-" * 40)
    if is_match:
        print("CONGRATS!!! You're a MATCHHHHHH (go confess) 🎉🔥❤️")
    elif not crush_has_used_program:
        print("Your crush hasn't used this program yet. Fingers crossed they type your name too... 🤫✨")
    else:
        print("Sorry. Not a match :(. 💔")

if __name__ == "__main__":
    main()
