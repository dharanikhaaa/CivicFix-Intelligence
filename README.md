# CivicFix-Intelligence
Budget-aware infrastructure repair planning
# CivicFix — Smart Civic Issue Management

CivicFix is a civic infrastructure management application built with Python and Streamlit. It helps organize public issue reports, prioritize repairs, and track progress within a limited budget.

## Features

- **Interactive Dashboard:** View complaint statistics and charts.
- **Issue Explorer:** Browse reported issues and priority scores.
- **Complaint Submission:** Submit civic issues with location and severity details.
- **Duplicate Detection:** Flag potentially duplicate reports for review.
- **Issue Management:** Track complaints through Open, In Progress, and Resolved statuses.
- **Budget Optimization:** Recommend a combination of repairs within a specified budget.
- **Infrastructure Network:** Visualize relationships between issues and locations.
- **SQLite Storage:** Persist submitted complaints and status updates.

## Technology Stack

- Python
- Streamlit
- Pandas
- SQLite
- NetworkX
- Matplotlib

## Project Structure

```text
civicfix/
├── app.py
├── data.py
├── database.py
├── duplicate_detector.py
├── budget_optimizer.py
├── graph_model.py
├── optimizer.py
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd civicfix
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run CivicFix

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## Database

CivicFix uses SQLite to store submitted complaints and status updates. The database file is generated locally by the application.

## Future Improvements

- Interactive geographic maps
- Improved duplicate detection
- User authentication and role-based access
- Enhanced repair scheduling
- Online deployment

## Disclaimer

CivicFix is a prototype for civic issue management. Repair estimates and priority scores are decision-support tools and should be reviewed by the relevant authorities.

## Author

CATALYX.
