# Team Workflow Guide — Using Google Colab with GitHub (Private Repo)

Welcome! This guide explains how our team collaborates using:

- **Google Colab**  
- **GitHub (Private Organization Repository)**  
- **Personal Access Tokens (PAT)**  
- **A shared secure workflow**

This ensures all members can safely pull, edit, commit, and push code without conflicts.

---

#  1. Requirements

Each team member must have:

✔ GitHub account  
✔ Personal Access Token (PAT)  
✔ Access to the organization repo  
✔ Google Colab  

---

#  2. Repository Folder Structure

When you clone the repo, Colab creates this folder automatically:



All your project files **must be placed inside this folder** so Git can track them.

---

#  3. Recommended Workflow Overview

Every time you open Colab:

1 Set Git identity  
2 Log in with GitHub username + token  
3 Clone the repo (first time only)  
4 Pull latest updates  
5 Commit and push your work  

Details below.

---

#  4. Step-by-Step Instructions

## Step 1 — Configure Git (Required every session)

```python
from getpass import getpass

email = input("Enter your GitHub email: ")
name = input("Enter your GitHub name: ")

!git config --global user.email "{email}"
!git config --global user.name "{name}"

print("Git identity configured!")

```

## Step 2 — Login with GitHub Username + Token (Hidden)

```python
from getpass import getpass

print("Enter your GitHub credentials (hidden):")
username = getpass("GitHub username: ")
token = getpass("GitHub Personal Access Token: ")

repo_url = f"https://{username}:{token}@github.com/Data-Visualization-Project/Data-Visualization-Final-Project.git"
print("Credentials stored securely.")

```

## Step 3 — Clone the Repository (First Time Only)

```python
!git clone $repo_url
%cd Data-Visualization-Final-Project

If you already cloned it earlier, simply return to the folder:

```python
%cd /content/Data-Visualization-Final-Project


```

##  Step 4 — Pull Latest Changes Before Working

```python
!git pull $repo_url main
(This prevents merge conflicts.)

```

##  Step 5 — Unzip Dataset from GitRepo

```python
!unzip /content/Data-Visualization-Final-Project/datasetV.zip

Everything you want to push must now appear inside:

/content/Data-Visualization-Final-Project

```

##  Step 6 — Stage and Commit Your Work

```python

%cd /content/Data-Visualization-Final-Project

!git add .
!git commit -m "Describe your update here"

```

##  Step 7 — Push to GitHub

```python
!git push $repo_url main

Your changes will now show up in the GitHub repository.

```

