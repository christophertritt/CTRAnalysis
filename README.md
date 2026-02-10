# Bellevue CTR Performance Dashboard

Official Analysis Edition for the City of Bellevue Transportation Department. Implements all calculations from the **CTR Data Analysis Guidelines** (Updated 3/24/2017).

## Features

- **Drive-Alone Rate (DAR)** – Weighted and unweighted metrics per official protocols  
- **Non-Drive-Alone Travel (NDAT)** – Trend and baseline comparisons  
- **Mode split** – Transit, carpool, active, telework  
- **TMP zone targets** – Past 3-cycle averages  
- **Compliance & quality** – Response rates and data quality  
- **Data export** – CSV download and summary tables  

## Quick start

1. **Clone or create the repo** (see [Connect to GitHub](#connect-to-github) below).
2. **Create a virtual environment and install dependencies:**

   ```bash
   cd CTR3
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Ensure the data file is present:**  
   `CTR_Master_Dataset_2003-2025_CLEANED.csv` in the project root.

4. **Run the dashboard:**

   ```bash
   streamlit run bellevue_ctr_dashboard_official_v3.py
   ```

   Open the URL shown in the terminal (usually http://localhost:8501).

## Connect to GitHub

### Option A: This folder is not yet a Git repo

1. **Create a new repository on GitHub**  
   Go to [github.com/new](https://github.com/new). Name it (e.g. `bellevue-ctr-dashboard`). Do **not** add a README, .gitignore, or license if you want to push this existing project.

2. **Initialize Git and push:**

   ```bash
   cd /path/to/CTR3
   git init
   git add .gitignore README.md requirements.txt bellevue_ctr_dashboard_official_v3.py Official_Dashboard_Implementation_Guide.md CTR_Master_Dataset_2003-2025_CLEANED.csv
   git commit -m "Initial commit: Bellevue CTR dashboard and docs"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

   Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub username and repo name.

### Option B: This folder is already a Git repo

1. **Create a new repository on GitHub** (same as above).

2. **Add the remote and push:**

   ```bash
   cd /path/to/CTR3
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git add .gitignore README.md requirements.txt bellevue_ctr_dashboard_official_v3.py Official_Dashboard_Implementation_Guide.md
   git add CTR_Master_Dataset_2003-2025_CLEANED.csv   # omit if you ignore CSV via .gitignore
   git commit -m "Add dashboard, requirements, and GitHub setup"
   git branch -M main
   git push -u origin main
   ```

### Authentication

- **HTTPS:** Use a [Personal Access Token](https://github.com/settings/tokens) as the password when Git asks.
- **SSH:** Use an SSH URL for `origin` and ensure your SSH key is added to GitHub:
  ```bash
  git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
  ```

## Deploy (optional)

- **Streamlit Community Cloud:** Push to GitHub, then connect the repo at [share.streamlit.io](https://share.streamlit.io). Set the main file to `bellevue_ctr_dashboard_official_v3.py`. If the CSV is in the repo, the app will run; otherwise add the dataset via Streamlit’s secrets or another data source.

## Documentation

See **Official_Dashboard_Implementation_Guide.md** for implementation details, formulas, and dashboard structure.

## Data

- **Source:** CTR Master Dataset 2003–2025 (cleaned).  
- **Location:** `CTR_Master_Dataset_2003-2025_CLEANED.csv` in the project root.  
- If the file is large or sensitive, add `CTR_Master_Dataset_*.csv` to `.gitignore` and document how to obtain the file in this README.

---

City of Bellevue Transportation Department · CTR Program · Dashboard v3.0
