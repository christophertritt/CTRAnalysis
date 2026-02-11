# Bellevue CTR Performance Dashboard

Official Analysis Edition for the City of Bellevue Transportation Department. Implements all calculations from the **CTR Data Analysis Guidelines** (Updated 3/24/2017).

## Features

- **🔒 Password Protection** – Secure login system to protect dashboard access
- **Drive-Alone Rate (DAR)** – Weighted and unweighted metrics per official protocols  
- **Non-Drive-Alone Travel (NDAT)** – Trend and baseline comparisons  
- **Mode split** – Transit, carpool, active, telework  
- **TMP zone targets** – Past 3-cycle averages  
- **Compliance & quality** – Response rates and data quality  
- **Data export** – CSV download and summary tables  

## Quick start

### Automated Setup (Recommended)

```bash
./start.sh
```

This script will:
- Check Python installation
- Create and activate virtual environment
- Install all dependencies
- Verify data file exists
- Launch the dashboard

### Manual Setup

1. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Ensure the data file is present:**  
   `CTR_Master_Dataset_2003-2025_CLEANED.csv` in the project root
   (See [DATA_DICTIONARY.md](DATA_DICTIONARY.md) for column definitions)

3. **Run the dashboard:**

   ```bash
   streamlit run bellevue_ctr_dashboard_official_v3.py
   ```

   Or use the Makefile:
   ```bash
   make run
   ```

   Open the URL shown in the terminal (usually http://localhost:8501)

## Security & Authentication

The dashboard includes password protection to restrict access. On first load, you'll see a login page.

### Default Credentials (Development)
**⚠️ Change these immediately for production use!**

- **Admin Account:** Username: `admin` / Password: `bellevue2026`
- **Viewer Account:** Username: `viewer` / Password: `ctr2026`

### Changing Passwords

1. **Open [auth.py](auth.py)**
2. **Modify the `DEFAULT_USERS` dictionary:**
   ```python
   DEFAULT_USERS = {
       "yourusername": hash_password("yournewpassword"),
       "another_user": hash_password("anotherpassword"),
   }
   ```
3. **Save and restart the dashboard**

### Adding More Users

Edit the `DEFAULT_USERS` dictionary in [auth.py](auth.py):
```python
DEFAULT_USERS = {
    "admin": hash_password("secure_password_here"),
    "analyst1": hash_password("analyst_password"),
    "analyst2": hash_password("another_password"),
}
```

### Advanced Authentication

For production deployments with many users, consider:
- **streamlit-authenticator** library (user database with encryption)
- **OAuth integration** (Google, Microsoft)
- **LDAP/Active Directory** integration
- Store credentials in **secrets.toml** instead of code

### Disabling Authentication

If you need to disable authentication temporarily, comment out the auth check in [bellevue_ctr_dashboard_official_v3.py](bellevue_ctr_dashboard_official_v3.py):
```python
# if not auth.check_password():
#     st.stop()
```

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

- **[Official_Dashboard_Implementation_Guide.md](Official_Dashboard_Implementation_Guide.md)** - Implementation details, formulas, and dashboard structure
- **[DATA_DICTIONARY.md](DATA_DICTIONARY.md)** - Complete column definitions and data schemas
- **[AUTHENTICATION.md](AUTHENTICATION.md)** - Security setup, password management, and advanced authentication options

## Troubleshooting

### Data file not found
**Error:** `⚠️ Data file not found. Please ensure CTR_Master_Dataset_2003-2025_CLEANED.csv...`

**Solution:** Ensure `CTR_Master_Dataset_2003-2025_CLEANED.csv` is in the same directory as the Python script.

### Import errors
**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
source .venv/bin/activate  # Activate virtual environment first
pip install -r requirements.txt
```

### Port already in use
**Error:** `Port 8501 is already in use`

**Solution:**
```bash
# Kill existing Streamlit process
pkill -f streamlit
# Or use a different port
streamlit run bellevue_ctr_dashboard_official_v3.py --server.port 8502
```

### Slow performance
If the dashboard is slow to load:
- Check file size of CSV (should be < 10MB)
- Use the cached version (TTL: 1 hour)
- Consider filtering to fewer survey cycles
- Close other browser tabs

### Python version issues
Requires Python 3.8 or later. Check your version:
```bash
python --version
```

## Development

### Makefile Commands
```bash
make help      # Show all available commands
make install   # Install dependencies
make run       # Run the dashboard
make clean     # Clean Python cache files
make lint      # Run linting checks
make format    # Format code with black
```

### Code Quality
The codebase follows PEP 8 style guidelines. Run linting before committing:
```bash
make lint
```

## Data

- **Source:** CTR Master Dataset 2003–2025 (cleaned).  
- **Location:** `CTR_Master_Dataset_2003-2025_CLEANED.csv` in the project root.  
- If the file is large or sensitive, add `CTR_Master_Dataset_*.csv` to `.gitignore` and document how to obtain the file in this README.

---

City of Bellevue Transportation Department · CTR Program · Dashboard v3.0
