#  Subscription Tracker AI

A simple Python script to track your upcoming subscription renewals and alert you before they are due. Perfect for avoiding surprise charges.

# Features
- Read subscriptions from a local `subscription.json` file.
- Automatically checks for due subscriptions every 6 hours.
- Designed to run in the background using `nohup`.
- No external files or database required.

# Requirements
- Python 3.8+
- A virtual environment (recommended)
- `subscription.json` file in the project root.

#  Example Subscriptions
json
Copy
Edit
[
  {
    "name": "Spotify",
    "renewal_date": "2025-05-15"
  },
  {
    "name": "Netflix",
    "renewal_date": "2025-05-12"
  }
]

# Run the Script
For One-Time Run:

python3 subscription_tracker.py


# For Background (Persistent) Run:

nohup python3 subscription_tracker.py &
tail -f nohup.out


# Output
Alerts for upcoming subscriptions due within 3 days.

Logs saved in nohup.out when run with nohup.

# Tips
Use ps aux | grep subscription_tracker.py to check if it’s running.

Use kill <PID> to stop it if needed.

# Author
Abhinav Choudhary

