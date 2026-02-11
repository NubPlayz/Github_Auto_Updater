import git
import os
import zipfile
import shutil
import requests
import json
from datetime import datetime
from pathlib import Path
import checker 


SKIP_DIRS = {".git", "backups", "__pycache__"}
EXE_STATE_FILE = "exe_state.json"


def load_exe_state():
    if not os.path.exists(EXE_STATE_FILE):
        return {}
    with open(EXE_STATE_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_exe_state(data):
    with open(EXE_STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)
        
def create_zip_backup(local_path):
    repo_name = Path(local_path).name
    backup_root = Path("backups").absolute() / f"{repo_name}_Source"
    backup_root.mkdir(parents=True, exist_ok=True)
    existing = sorted(backup_root.glob("*.zip"), key=os.path.getctime)
    if len(existing) >= 3:
        for old in existing[:len(existing)-2]: old.unlink()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = backup_root / f"backup_{timestamp}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(local_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for file in files:
                full_p = os.path.join(root, file)
                zipf.write(full_p, os.path.relpath(full_p, local_path))

def backup_single_file(file_path):
    if not os.path.exists(file_path): return
    file_name = os.path.basename(file_path)
    backup_root = Path("backups").absolute() / f"{file_name}_EXE"
    backup_root.mkdir(parents=True, exist_ok=True)
    existing = sorted(backup_root.glob("*"), key=os.path.getctime)
    if len(existing) >= 3:
        for old in existing[:len(existing)-2]: old.unlink()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(file_path, backup_root / f"{timestamp}_{file_name}")

def run_safe_sync(local_path, github_url, mode):
    try:
        os.makedirs(local_path, exist_ok=True)
        yield 5, "VALIDATING REPOSITORY"

        owner, repo_name = checker.parse_repo_url(github_url)
        branch = checker.get_default_branch(owner, repo_name)

        if not branch:
            yield 100, "ERROR: Repository not found or inaccessible"
            return

        yield 15, "REPOSITORY VERIFIED"

        
        if mode in ["Source Code", "Both"]:
            yield 30, "SYNCING SOURCE CODE"

            is_git = os.path.exists(os.path.join(local_path, ".git"))

            if not is_git:
                yield 45, "CLONING REPOSITORY"
                git.Repo.clone_from(github_url, local_path)

                if not os.path.exists(os.path.join(local_path, ".git")):
                    yield 100, "ERROR: Clone failed"
                    return

                yield 60, "SOURCE CLONED"

            else:
                repo = git.Repo(local_path)
                origin = repo.remotes.origin

                yield 50, "FETCHING REMOTE CHANGES"
                origin.fetch()

                local_commit = repo.head.commit.hexsha
                remote_commit = repo.commit(f'origin/{branch}').hexsha

                if local_commit == remote_commit:
                    yield 60, "SOURCE UP TO DATE"
                else:
                    yield 60, "UPDATING REPOSITORY"
                    create_zip_backup(local_path)
                    repo.git.reset('--hard', f'origin/{branch}')
                    yield 70, "SOURCE UPDATED"


     
            if mode in ["Latest Release (.exe)", "Both"]:
                yield 70, "CHECKING LATEST RELEASE"

                release_info = checker.get_latest_release_info(owner, repo_name)
                if not release_info:
                    yield 100, "ERROR: Failed to fetch release info"
                    return

                rel_id, tag, asset_url, asset_name = release_info

                if not asset_url:
                    yield 85, "NO EXE ASSET FOUND"
                else:
                    state = load_exe_state()
                    repo_key = github_url

                    if state.get(repo_key) == tag:
                        yield 85, "EXE UP TO DATE"
            else:
                local_file = os.path.join(local_path, asset_name)

                yield 80, f"DOWNLOADING {tag}"
                backup_single_file(local_file)

                resp = requests.get(asset_url, stream=True)
                if resp.status_code != 200:
                    yield 100, "ERROR: Failed to download release"
                    return

                with open(local_file, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)

                state[repo_key] = tag
                save_exe_state(state)

                yield 90, "EXE UPDATED"


    except Exception as e:
        yield 100, f"ERROR: {str(e)}"

