from github import Github
import os
import time
from pprint import pprint
import re
import time
from datetime import timedelta
from datetime import date
import json
from datetime import datetime
from slack_sdk.webhook import WebhookClient

issues_organization = os.environ.get("issues_organization")
issues_repository_list = os.environ.get("issues_repository_list")
git_token = os.environ.get("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")
issues_labels = os.environ.get("issues_labels")
reports_slack_webhook_url = os.environ.get("reports_slack_webhook_url")
slack_users = os.environ.get("slack_users")

repo_list = issues_repository_list.split(",")
webhook = WebhookClient(reports_slack_webhook_url)

# Github Enterprise with custom hostname
g = Github(base_url="https://github.ibm.com/api/v3", login_or_token=git_token)

date_now_more_15_days = (datetime.now() + timedelta(days=15) ).strftime('%Y-%m-%d')

def due_check(repo):
    overdue_list = []
    due_soon_list = []
    issue_labels = issues_labels.split(",")
    issues = repo.get_issues(state="open",labels=issue_labels)
    for issue in issues:
        for label in issue.labels:
            find_due_label = re.search("dueDate:", label.name)
            if find_due_label:
                due_date = label.name.split(":")[1]
                if due_date <  date_now_more_15_days:
                    if due_date < datetime.now().strftime('%Y-%m-%d'):
                        overdue_list.append("\n "+issue.html_url)
                    else:
                        due_soon_list.append("\n "+issue.html_url)

    return overdue_list, due_soon_list

def slack_alert_overdue(overdue_list, repo_name):

    if len(overdue_list) != 0:
        overdue_list_str = ' '.join(map(str, overdue_list))
        if slack_users != '':
            slack_content = slack_users+"OverDue List in "+repo_name+" :"+overdue_list_str
        else:
            slack_content = "OverDue List in "+repo_name+" :"+overdue_list_str
    else:
        if slack_users != '':
            slack_content = slack_users+"No Overdues in "+repo_name
        else:
            slack_content = "No Overdues in "+repo_name
    if reports_slack_webhook_url != "":
        webhook.send(text=slack_content)
    else:
        print("Din't send notifications to slack as ENV value to slack-webhook is not set")

def slack_alert_duesoon(due_soon_list, repo_name):

    if len(due_soon_list) != 0:
        due_soon_list_str = ' '.join(map(str, due_soon_list))
        if slack_users != '':
            slack_content = slack_users+"Due Soon(within 15 days) List in "+repo_name+" :"+due_soon_list_str
        else:
            slack_content = "Due Soon(within 15 days) List in "+repo_name+" :"+due_soon_list_str
    else:
        if slack_users != '':
            slack_content = slack_users+"No Due Soon in 15 days in "+repo_name
        else:
            slack_content = "No Due Soon in 15 days in "+repo_name
    if reports_slack_webhook_url != "":
        webhook.send(text=slack_content)
    else:
        print("Din't send notifications to slack as ENV value to slack-webhook is not set")

def main():
    for each_repo in repo_list:
        repo_name = issues_organization + '/' + each_repo
        repo = g.get_repo(repo_name)
        overdue_list, due_soon_list = due_check(repo)
        slack_alert_overdue(overdue_list, repo_name)
        slack_alert_duesoon(due_soon_list, repo_name)

main()
