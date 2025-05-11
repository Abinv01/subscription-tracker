import json
import smtplib
import time
from datetime import datetime
from email.message import EmailMessage
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ALERT_RECIPIENT = os.getenv("ALERT_RECIPIENT")

# Constants
ALERT_DAYS = 5
MONTHS_TO_CHECK = 12
SLEEP_HOURS = 6
SUBSCRIPTION_FILE = "subscription.json"  #  CORRECTED

def load_subscriptions():
    """Load the subscription list from JSON file."""
    try:
        with open(SUBSCRIPTION_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f" {SUBSCRIPTION_FILE} not found.", flush=True)
        return []
    except json.JSONDecodeError as e:
        print(f" Error parsing {SUBSCRIPTION_FILE}: {e}", flush=True)
        return []

def get_due_dates(start_date, cycle, count):
    for i in range(count):
        if cycle == "monthly":
            yield start_date + relativedelta(months=i)
        elif cycle == "yearly" or cycle == "annually":
            yield start_date + relativedelta(years=i)

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
        print(f" Email alert sent to {to_email}: {subject}", flush=True)
    except Exception as e:
        print(f" Failed to send email: {e}" , flush=True)

def check_subscriptions():
    today = datetime.today().date()
    subscriptions = load_subscriptions()

    if not subscriptions:
        return

    for sub in subscriptions:
        name = sub.get("name")
        date_str = sub.get("next_due_date")
        cycle = sub.get("cycle", "monthly").lower()

        if not name or not date_str:
            print(f" Skipping invalid subscription entry: {sub}" , flush=True)
            continue

        try:
            start_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f" Invalid date format for {name}: {date_str}" , flush=True)
            continue

        for due_date in get_due_dates(start_date, cycle, MONTHS_TO_CHECK):
            days_left = (due_date - today).days
            if 0 <= days_left <= ALERT_DAYS:
                subject = f" {name} is due in {days_left} days!"
                body = f"Your {name} subscription is due on {due_date} ({days_left} days left)."
                send_email_alert(subject, body, ALERT_RECIPIENT)
                break  # Alert only once per cycle

def main():
    while True:
        print(f"\n Checking subscriptions at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" , flush=True)
        check_subscriptions()
        print(f" Sleeping for {SLEEP_HOURS} hours...\n" , flush=True)
        time.sleep(SLEEP_HOURS)
        time.sleep(SLEEP_HOURS * 3600)

if __name__ == "__main__":
    main()
