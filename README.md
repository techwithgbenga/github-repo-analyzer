# GitHub Repository Analyzer & Trends Tracker

This project monitors GitHub repositories by fetching key metrics (stars, forks, open issues, watchers) via the GitHub API. It logs these metrics in a CSV file, generates trend plots, and sends alert emails if defined thresholds are breached.

## Features

- **GitHub Data Fetching:** Uses the GitHub API with a personal access token.
- **Historical Data Logging:** Saves metrics with timestamps to a CSV file.
- **Trend Visualization:** Generates plots of repository metrics over time.
- **Email Alerts:** Notifies you when repository metrics fall outside configured thresholds.
- **Scheduling:** Runs the monitoring process periodically (every 30 minutes by default).

## Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/techwithgbenga/github-repo-analyzer.git
   cd github-repo-analyzer
```
2. Install Dependencies:
```bash
pip install -r requirements.txt
```
3. Configure the Application:
Edit config.json:
- Add the repository names (in owner/repo format) that you want to monitor.
- Insert your GitHub personal access token.
- Set up email credentials if you want to use alert emails.
- Adjust any alert thresholds as needed.
- Security Tip: Never commit your GitHub token or email credentials to a public repository. Consider using environment variables or secret management tools in production.

4. Run the Application:
```bash
python repo_analyzer.py
```
---

## Future Improvements
- Add a web dashboard for real-time monitoring.
- Integrate more repository metrics and historical analysis.
- Support additional notification channels (e.g., Slack or SMS).
- Pull requests and contributions are welcome!

---

## Summary

This GitHub Repository Analyzer & Trends Tracker project offers developers a powerful tool to monitor repository health, track trends over time, and receive alerts about important changes. Its modular design and detailed configuration make it an ideal open-source resource to share with the community.

Would you like to add any additional functionalities, such as integrating Slack notifications, more advanced data analytics, or a live dashboard?
