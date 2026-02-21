# GitHubSync
<p align="left"> <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white" /> <img src="https://img.shields.io/badge/Streamlit-1.54.0-FF4B4B?logo=streamlit&logoColor=white" /> <img src="https://img.shields.io/badge/GitPython-3.1.46-orange?logo=git&logoColor=white" /> <img src="https://img.shields.io/badge/Requests-2.32.5-green?logo=python&logoColor=white" /> <img src="https://img.shields.io/badge/PyInstaller-Bundled-blueviolet" /> <img src="https://img.shields.io/badge/Git-Automation-F05032?logo=git&logoColor=white" /> </p>





**GitHubSync** is a clean and reliable Python tool that automatically updates your local GitHub repositories from their remote sources.

It works for both normal cloned repositories and packaged executables, and it always creates a safe backup before making any changes.



## Features

- Batch sync multiple repositories at once
- Automatic backup before every update
- Rotating backup system (keeps only the last 3 backups,per repo)
- Works as a normal Python script or as a standalone .exe
- Simple and clean Streamlit web interface

---

# Local / Cloned Version

### Installation
```markdown


```bash
git clone https://github.com/your-username/GitHubSync.git
cd GitHubSync
```

Create a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Required Versions

- GitPython == 3.1.46
- requests == 2.32.5
- streamlit == 1.54.0

### Run the Application

```bash
streamlit run app.py
```

The app will open in your default browser.



## Backup & Failsafe System

Before every synchronization operation:

> A full backup is created automatically  
> The repository (and executable if present) is zipped with a timestamp  
> Backups are stored in the `backups/` folder

**Rotation Policy**  
> Maximum of 3 backups kept per target  
> Oldest backup is automatically deleted when the limit is exceeded



# Executable (Packaged) Version

You can package the app into a single `.exe` using PyInstaller.

## Behavior Differences from Cloned Version

**1. Launch Mode**

- No Python environment required.

- Automatically opens in the system’s default browser.

- Runs as a packaged Streamlit application.

**2. Backup Location**

Backups are stored relative to the executable location:
```
<exe_directory>/backups/
```
If the executable is placed outside the cloned project structure, backups are created alongside the .exe file inside a backups directory.

**3. Rotation Policy**

- Identical to the cloned version:

- Maximum 3 backups retained.

- Automatic cleanup of oldest archive.

- Both repositories and executable states included when configured.




# Technical Details

## Technical Architecture

### Core Libraries Used
```
import git
import os
import zipfile
import shutil
import requests
import json
from datetime import datetime
from pathlib import Path
import checker

```

### Functional Components



- Git Operations – Managed via GitPython

- Update Validation – Custom logic through checker

- Backup System – Zip-based snapshotting with rotation

- Filesystem Control – Path-safe operations using Path

- Remote Checks – HTTP verification using requests

- Configuration Handling – JSON-based storage

### Key Features

- Batch synchronization of multiple repositories

- Executable-based deployment support

- Automatic pre-sync backup generation

- Rotation-based backup limit (max 3)

- Timestamped compressed archives

- Cloud-to-local update alignment

- No manual Git command requirement for end users

---

GitHubSync was built to keep your repositories up to date with zero manual effort and maximum safety.

Feel free to open issues or pull requests!
```

an app to manage your outdated github repositories and exe.
