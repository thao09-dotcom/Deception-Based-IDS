from flask import Flask, render_template
from datetime import datetime
import json
import os

app = Flask(__name__)

@app.route("/")
def dashboard():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(base_dir, "logs", "events.log")

    events = []

    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            for line in f:
                try:
                    event = json.loads(line)

                    # Format timestamp
                    raw_time = event.get("timestamp")
                    if raw_time:
                        dt = datetime.fromisoformat(raw_time)
                        event["formatted_time"] = dt.strftime("%m-%d-%Y %I:%M:%S %p")
                    else:
                        event["formatted_time"] = "N/A"

                    events.append(event)
                except:
                    continue

    # Status
    total = len(events)
    failed = sum(1 for e in events if e.get("status") == "failed")
    detections = sum(1 for e in events if e.get("event_type") == "detection")
    honeypot = sum(1 for e in events if "honeypot" in e.get("event_type", ""))

    # List events in desc order by time
    events = list(reversed(events))

    return render_template(
        "dashboard.html",
        events=events,
        total=total,
        failed=failed,
        detections=detections,
        honeypot=honeypot
    )


if __name__ == "__main__":
    app.run(port=5001, debug=True)