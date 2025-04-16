import requests
import json
import csv
import os
import logging
import schedule
import time
import matplotlib.pyplot as plt
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load configuration
with open("config.json", "r") as file:
    config = json.load(file)

REPOSITORIES = config["repositories"]
GITHUB_TOKEN = config["github"]["token"]
EMAIL_CONFIG = config.get("email", {})
CSV_FILE = config.get("csv_file", "repo_stats.csv")
PLOT_FOLDER = config.get("plot_folder", "plots")
ALERT_THRESHOLDS = config.get("alert_thresholds", {})

# Logging setup
logging.basicConfig(filename="repo_analyzer.log", 
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

def send_email_alert(subject, body):
    """Send an email alert using SMTP."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_CONFIG["sender"]
        msg["To"] = EMAIL_CONFIG["receiver"]
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["port"], context=context) as server:
            server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
            server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())
        logging.info("Alert email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def log_repo_data(timestamp, repo_full_name, stars, forks, open_issues, watchers):
    """Append repository data to the CSV log file."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Repository", "Stars", "Forks", "Open Issues", "Watchers"])
        writer.writerow([timestamp, repo_full_name, stars, forks, open_issues, watchers])

def plot_repo_data(repo_full_name):
    """Read CSV data for a repository, generate and save a trend plot."""
    timestamps, stars, forks, open_issues, watchers = [], [], [], [], []

    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Repository"] == repo_full_name:
                    timestamps.append(datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S"))
                    stars.append(int(row["Stars"]))
                    forks.append(int(row["Forks"]))
                    open_issues.append(int(row["Open Issues"]))
                    watchers.append(int(row["Watchers"]))

        if timestamps:
            os.makedirs(PLOT_FOLDER, exist_ok=True)
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, stars, label="Stars", marker="o")
            plt.plot(timestamps, forks, label="Forks", marker="o")
            plt.plot(timestamps, open_issues, label="Open Issues", marker="o")
            plt.plot(timestamps, watchers, label="Watchers", marker="o")
            plt.xlabel("Time")
            plt.ylabel("Count")
            plt.title(f"Repository Metrics Over Time: {repo_full_name}")
            plt.legend()
            plt.grid(True)
            plot_path = os.path.join(PLOT_FOLDER, f"{repo_full_name.replace('/', '_')}_trend.png")
            plt.savefig(plot_path)
            plt.close()
            logging.info(f"Plot saved for {repo_full_name} at {plot_path}")
    except Exception as e:
        logging.error(f"Error plotting data for {repo_full_name}: {e}")

def fetch_repo_data(repo_full_name):
    """Fetch repository data from GitHub API."""
    url = f"https://api.github.com/repos/{repo_full_name}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code == 200:
        data = response.json()
        stars = data.get("stargazers_count", 0)
        forks = data.get("forks_count", 0)
        open_issues = data.get("open_issues_count", 0)
        watchers = data.get("subscribers_count", 0)
        return stars, forks, open_issues, watchers
    else:
        logging.error(f"Failed to fetch data for {repo_full_name}: HTTP {response.status_code}")
        return None

def check_and_alert(repo_full_name, current_data):
    """Check current repository data against thresholds and send alerts if needed."""
    thresholds = ALERT_THRESHOLDS.get(repo_full_name, {})
    alerts = []
    
    stars, forks, open_issues, watchers = current_data

    if "min_stars" in thresholds and stars < thresholds["min_stars"]:
        alerts.append(f"Stars dropped below threshold: {stars} < {thresholds['min_stars']}")
    if "max_open_issues" in thresholds and open_issues > thresholds["max_open_issues"]:
        alerts.append(f"Open issues exceed threshold: {open_issues} > {thresholds['max_open_issues']}")
    
    if alerts and EMAIL_CONFIG:
        subject = f"Alert for {repo_full_name}"
        body = f"Repository: {repo_full_name}\n" + "\n".join(alerts)
        send_email_alert(subject, body)

def monitor_repositories():
    """Loop over repositories to fetch, log, plot data and check for alerts."""
    logging.info("Starting repository data monitoring cycle...")
    for repo in REPOSITORIES:
        current_data = fetch_repo_data(repo)
        if current_data:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_repo_data(timestamp, repo, *current_data)
            plot_repo_data(repo)
            check_and_alert(repo, current_data)
            logging.info(f"Processed data for {repo}")
        else:
            logging.warning(f"Skipped {repo} due to data fetch failure.")

# Schedule the monitoring job (e.g., every 30 minutes)
schedule.every(30).minutes.do(monitor_repositories)

if __name__ == "__main__":
    logging.info("Starting GitHub Repository Analyzer & Trends Tracker...")
    monitor_repositories()  # Initial run
    while True:
        schedule.run_pending()
        time.sleep(1)
