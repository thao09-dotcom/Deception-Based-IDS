import os
import time
import json
from datetime import datetime

from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = "secret_key"

# Testing successful creds
VALID_USERNAME = "admin"
VALID_PASSWORD = "password"


def log_event(event_type, username=None, status=None, details=None):
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "username": username,
        "status": status,
        "details": details
    }

    # Get absolute path to project directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, "logs")

    # Create logs folder if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "events.log")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


@app.route("/", methods=["GET", "POST"])
def login():
    # If flagged then force honeypot
    if session.get("is_suspicious"):
        log_event("honeypot_access", status="forced_redirect")
        return redirect(url_for("decoy"))

    message = ""
    msg_type = "success"

    if "attempts" not in session:
        session["attempts"] = []

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        current_time = time.time()

        # Keep only attempts from the last 30 secs
        recent_attempts = [
            attempt
            for attempt in session["attempts"]
            if current_time - attempt["time"] <= 30
        ]
        session["attempts"] = recent_attempts

        # If success
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            log_event("login_attempt", username, "success")

            message = "Login successful"
            msg_type = "success"

            # Clear attempts after successful login
            session["attempts"] = []

        # If fail
        else:
            session["attempts"].append({
                "username": username,
                "time": current_time
            })
            session.modified = True

            log_event(
                "login_attempt",
                username,
                "failed",
                f"Failed login within 30-second window. Total recent attempts: {len(session['attempts'])}"
            )

            message = "Login failed."
            msg_type = "error"

            # Brute force pattern 1: Same account > 5 within 30 secs
            same_user_attempts = [
                attempt for attempt in session["attempts"]
                if attempt["username"] == username
            ]

            if len(same_user_attempts) > 5:
                log_event(
                    "detection",
                    username,
                    "triggered",
                    "Pattern detected: repeated failed attempts against same account within 30 seconds"
                )
                session["is_suspicious"] = True
                return redirect(url_for("decoy"))

            # Brute force pattern 2: Total attempts > 5 across different usernames within 30 secs
            unique_usernames = {attempt["username"] for attempt in session["attempts"]}

            if len(session["attempts"]) > 5 and len(unique_usernames) > 1:
                log_event(
                    "detection",
                    None,
                    "triggered",
                    "Pattern detected: multiple failed attempts across different usernames within 30 seconds"
                )
                session["is_suspicious"] = True
                return redirect(url_for("decoy"))

        print("Recent attempts:", session["attempts"])

    return render_template("login.html", message=message, msg_type=msg_type)


# Honeypot UI to decoy.html
@app.route("/decoy")
def decoy():
    log_event("honeypot_access", status="entered_decoy")
    return render_template("decoy.html")


# Log actions within honeypot env
@app.route("/log_action", methods=["POST"])
def log_action():
    data = request.json or {}
    action = data.get("action")

    log_event("honeypot_action", status="interaction", details=action)

    return jsonify({"status": "logged"})


# Reset for clean showcasing purposes
@app.route("/reset")
def reset():
    session.clear()

    # Clear log file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(base_dir, "logs", "events.log")

    if os.path.exists(log_file):
        open(log_file, "w").close()

    return "Session and logs reset"


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)