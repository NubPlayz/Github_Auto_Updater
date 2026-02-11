import streamlit as st
import re
import updater
from datetime import datetime
from nodes_store import load_nodes, save_nodes


st.set_page_config(
    page_title="GitHub Repo Updater",
    layout="wide",
    initial_sidebar_state="expanded"
)


if "targets" not in st.session_state:
    st.session_state.targets = load_nodes()

if "system_state" not in st.session_state:
    st.session_state.system_state = "IDLE"


def is_valid_github(url):
    return re.match(r"https?://github\.com/[\w-]+/[\w.-]+", url)

def summarize_run(gen):
    msgs = []
    for _, msg in gen:
        if msg:
            msgs.append(msg.upper())

    if any("ERROR" in m for m in msgs):
        return "error", ["Failed"]

    if any("UPDATED" in m for m in msgs):
        return "success", ["Updated"]

    if any("CLONED" in m for m in msgs):
        return "success", ["Cloned"]

    if any("UP TO DATE" in m for m in msgs):
        return "success", ["Up to date"]

    if any("NO EXE" in m for m in msgs):
        return "warning", ["No EXE found"]

    return "success", ["Completed"]

def run_with_loading(gen):
    progress = st.progress(0)
    collected = []

    for pct, msg in gen:
        progress.progress(min(pct, 100))
        if msg:
            collected.append(msg)

    progress.empty()
    return summarize_run([(None, m) for m in collected])

with st.sidebar:
    st.header("Add Repository")
    
    with st.form("add_node", clear_on_submit=True):
        name = st.text_input("Name", placeholder="my-project")
        repo = st.text_input("GitHub URL", placeholder="https://github.com/user/repo")
        path = st.text_input("Local Path", placeholder="C:/projects/my-project")
        mode = st.selectbox(
            "Sync Mode",
            ["Source Code", "Latest Release (.exe)", "Both"]
        )
        
        submitted = st.form_submit_button("Add Repository", use_container_width=True)
        
        if submitted:
            if name and path and is_valid_github(repo):
                st.session_state.targets.append({
                    "name": name,
                    "repo": repo,
                    "path": path,
                    "mode": mode
                })
                save_nodes(st.session_state.targets)
                st.success(f"Added {name}")
                st.rerun()
            else:
                st.error("Please fill in all fields with valid data")

st.title("GitHub Repository Updater")
st.caption("Manage and synchronize your GitHub repositories")

if st.session_state.system_state == "SYNCING":
    st.info("Synchronizing repositories...")
elif st.session_state.system_state == "DONE":
    st.success("Synchronization complete")

if st.session_state.targets:
    if st.button("Sync All Repositories", type="primary", use_container_width=True):
        st.session_state.system_state = "SYNCING"
        
        with st.spinner("Syncing all repositories..."):
            for node in st.session_state.targets:
                try:
                    status, messages = run_with_loading(
                        updater.run_safe_sync(
                            node["path"],
                            node["repo"],
                            node["mode"]
                        )
                    )
                except Exception:
                    status, messages = "error", ["Failed"]
                
                node["last_result"] = {
                    "status": status,
                    "messages": messages
                }
        
        save_nodes(st.session_state.targets)
        st.session_state.system_state = "DONE"
        st.rerun()

if not st.session_state.targets:
    st.info("No repositories configured. Add one using the sidebar.")
else:
    st.subheader(f"Repositories ({len(st.session_state.targets)})")
    
    for idx, node in enumerate(st.session_state.targets):
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                st.write(f"**{node['name']}**")
                st.caption(f"{node['repo']}")
                st.caption(f"Path: {node['path']} | Mode: {node['mode']}")
            
            with col2:
                if st.button("Sync", key=f"sync_{idx}", use_container_width=True):
                    st.session_state.system_state = "SYNCING"
                    
                    with st.spinner(f"Syncing {node['name']}..."):
                        try:
                            status, messages = run_with_loading(
                                updater.run_safe_sync(
                                    node["path"],
                                    node["repo"],
                                    node["mode"]
                                )
                            )
                        except Exception:
                            status, messages = "error", ["Failed"]
                    
                    node["last_result"] = {
                        "status": status,
                        "messages": messages
                    }
                    
                    save_nodes(st.session_state.targets)
                    st.session_state.system_state = "DONE"
                    st.rerun()
            
            with col3:
                if st.button("Delete", key=f"del_{idx}", use_container_width=True):
                    st.session_state.targets.pop(idx)
                    save_nodes(st.session_state.targets)
                    st.rerun()
            
            if "last_result" in node:
                if node["last_result"]["status"] == "success":
                    st.success(" • ".join(node["last_result"]["messages"]))
                else:
                    st.error(" • ".join(node["last_result"]["messages"]))
            
            st.divider()

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
