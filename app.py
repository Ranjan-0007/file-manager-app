"""
Streamlit File Manager
-----------------------
A simple UI replacement for the original CLI create/read/update/delete
file-manager script. All files are sandboxed inside ./workspace.

Run with:
    streamlit run app.py
"""

import streamlit as st
from utils.file_operations import (
    list_files,
    create_file,
    read_file,
    overwrite_file,
    append_file,
    rename_file,
    delete_file,
    ensure_workspace,
)

st.set_page_config(page_title="File Manager", page_icon="📁", layout="centered")
ensure_workspace()

st.title("📁 File Manager")
st.caption("Create, read, update, and delete text files — safely sandboxed to a local `workspace/` folder.")

# --- Flash message shown once, right after a rerun --------------------------
# (st.success() called just before st.rerun() would otherwise be wiped out by
# the rerun before the user ever sees it, so we stash it in session_state
# and render it on the next run instead.)
if "flash" in st.session_state:
    flash_type, flash_msg = st.session_state.pop("flash")
    getattr(st, flash_type)(flash_msg)


def flash_and_rerun(success: bool, message: str):
    st.session_state["flash"] = ("success" if success else "error", message)
    st.rerun()


# --- Sidebar: navigation + live file browser -------------------------------
with st.sidebar:
    st.header("Menu")
    action = st.radio(
        "Choose an operation",
        ["Create", "Read", "Update", "Delete"],
        label_visibility="collapsed",
    )

    st.divider()
    st.subheader("Files in workspace")
    files = list_files()
    if files:
        for f in files:
            st.write(f"• {f}")
    else:
        st.write("_No files yet._")


# --- Create ------------------------------------------------------------
if action == "Create":
    st.subheader("Create a new file")
    filename = st.text_input("File name", placeholder="example.txt")
    content = st.text_area("Content", placeholder="Enter your content here...", height=150)
    if st.button("Create File", type="primary"):
        if not filename.strip():
            st.warning("Please enter a file name.")
        else:
            flash_and_rerun(*create_file(filename.strip(), content))

# --- Read ----------------------------------------------------------------
elif action == "Read":
    st.subheader("Read a file")
    files = list_files()
    if not files:
        st.info("No files in the workspace yet. Create one first.")
    else:
        filename = st.selectbox("Choose a file", files)
        if st.button("Read File", type="primary"):
            success, content = read_file(filename)
            if success:
                st.success(f"Showing contents of '{filename}':")
                st.code(content or "(file is empty)", language=None)
            else:
                st.error(content)

# --- Update ----------------------------------------------------------------
elif action == "Update":
    st.subheader("Update a file")
    files = list_files()
    if not files:
        st.info("No files in the workspace yet. Create one first.")
    else:
        filename = st.selectbox("Choose a file", files)
        operation = st.radio(
            "Operation",
            ["Overwrite", "Append", "Rename"],
            horizontal=True,
        )

        if operation == "Overwrite":
            content = st.text_area("New content (replaces existing content)", height=150)
            if st.button("Overwrite File", type="primary"):
                flash_and_rerun(*overwrite_file(filename, content))

        elif operation == "Append":
            content = st.text_area("Content to add to the end of the file", height=150)
            if st.button("Append to File", type="primary"):
                flash_and_rerun(*append_file(filename, content))

        elif operation == "Rename":
            new_filename = st.text_input("New file name")
            if st.button("Rename File", type="primary"):
                if not new_filename.strip():
                    st.warning("Please enter a new file name.")
                else:
                    flash_and_rerun(*rename_file(filename, new_filename.strip()))

# --- Delete ----------------------------------------------------------------
elif action == "Delete":
    st.subheader("Delete a file")
    files = list_files()
    if not files:
        st.info("No files in the workspace yet.")
    else:
        filename = st.selectbox("Choose a file to delete", files)
        st.warning(f"This will permanently delete **{filename}**.")
        if st.button("Delete File", type="primary"):
            flash_and_rerun(*delete_file(filename))