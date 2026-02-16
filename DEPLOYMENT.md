# Deployment Guide: Streamlit Cloud

This guide explains how to host your QA Issue Tracker on Streamlit Cloud.

## ⚠️ Important Note on Persistence
This app currently uses **SQLite** (`database.db`) and **Local File Storage** (`uploads/`).
**Streamlit Cloud is ephemeral**, meaning your database and uploaded files will be **deleted** every time the app reboots or you deploy any change.
*For a production version, you would need to switch to a cloud database (e.g., Google Sheets, Firestore, Supabase) and cloud storage (e.g., AWS S3).*

---

## Step 1: Push Code to GitHub

1.  **Initialize Git** (Already done locally):
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    ```

2.  **Create a New Repository on GitHub**:
    *   Go to [GitHub.com](https://github.com/new).
    *   Name it (e.g., `qa-issue-tracker`).
    *   Make it **Public** (or Private).
    *   Do **not** initialize with README/gitignore (we already have them).

3.  **Connect and Push**:
    *   Copy the URL of your new repo (e.g., `https://github.com/yourusername/qa-issue-tracker.git`).
    *   Run these commands in your terminal:
    ```bash
    git branch -M main
    git remote add origin <PASTE_YOUR_REPO_URL_HERE>
    git push -u origin main
    ```

## Step 2: Deploy on Streamlit Cloud

1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  Select your repository (`qa-issue-tracker`).
4.  **Branch**: `main`.
5.  **Main file path**: `app/app.py`.
6.  Click **"Deploy!"**.

## Step 3: Admin Setup (Post-Deploy)
Since the database is recreated on deploy, the default `admin` and `abhiraman` users will be created automatically by `init_db()` on the first run.
You can log in immediately after deployment.
