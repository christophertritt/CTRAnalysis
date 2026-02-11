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
