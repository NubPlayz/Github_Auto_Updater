import requests
import re

def parse_repo_url(url):
    match = re.search(r"github\.com/([\w-]+)/([\w.-]+)", url)
    if match:
        return match.group(1), match.group(2).replace(".git", "")
    raise ValueError("Invalid GitHub URL")

def get_default_branch(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("default_branch", "main")
    return "main"

def get_latest_release_info(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        release_id = data.get("id")
        tag_name = data.get("tag_name")
        assets = data.get("assets", [])
        for asset in assets:
            if asset['name'].endswith(".exe"):
                return release_id, tag_name, asset['browser_download_url'], asset['name']
    return None, None, None, None