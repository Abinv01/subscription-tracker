import json
import smtplib
import os
from datetime import datetime
from email.message import EmailMessage
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ALERT_RECIPIENT = os.getenv("ALERT_RECIPIENT")

# Settings
ALERT_DAYS = 5
MONTHS_TO_CHECK = 12

# Construct absolute path to subscriptions.json
script_dir = os.path.dirname(os.path.abspath(__file__))
subscription_path = os.path.join(script_dir, "subscription.json")

# Load subscriptions file
try:
    with open(subscription_path, "r") as f:
        subscriptions = json.load(f)
except FileNotFoundError:
    print(f"❌ subscriptions.json not found at: {subscription_path}")
    exit(1)
except json.JSONDecodeError as e:
    print(f"❌ Failed to parse subscriptions.json: {e}")
    exit(1)

# Get today's date
today = datetime.today().date()

# Generator to yield future due dates
def get_due_dates(start_date, cycle, count):
    for i in range(count):
        if cycle == "monthly":
            yield start_date + relativedelta(months=i)
        elif cycle == "annually":
            yield start_date + relativedelta(years=i)
        else:
            print(f"⚠️ Unknown billing cycle '{cycle}' — skipping.")
            break

# Send email alert
def send_email_alert(subject, body, to_email):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email alert sent to {to_email} for: {subject}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Main logic: check all subscriptions
for sub in subscriptions:
    name = sub["name"]
    try:
        start_date = datetime.strptime(sub["next_due_date"], "%Y-%m-%d").date()
    except ValueError:
        print(f"⚠️ Invalid date format for {name} — skipping.")
        continue

    cycle = sub.get("cycle", "monthly").lower()

    for due_date in get_due_dates(start_date, cycle, MONTHS_TO_CHECK):
        days_left = (due_date - today).days
        if 0 <= days_left <= ALERT_DAYS:
            subject = f"🔔 {name} is due soon!"
            body = f"Your {name} subscription is due in {days_left} days (on {due_date})."
            send_email_alert(subject, body, ALERT_RECIPIENT)
            break  # Only alert once per subscription
