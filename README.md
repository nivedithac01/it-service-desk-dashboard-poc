# IT Service Desk Analytics Dashboard

A Python-based analytics dashboard built with **Streamlit**, **Pandas**, and **Plotly** that demonstrates IT service desk operational intelligence for a financial services environment. The dashboard provides real-time visibility into incident management, SLA compliance, device lifecycle tracking, and Active Directory user provisioning.

---

## Overview

This proof-of-concept simulates an enterprise IT service desk supporting a global financial services organisation with trade floor and corporate environments. It generates realistic synthetic data covering:

- **5,000+ incident tickets** across categories like Trading Systems (Bloomberg, Reuters), Office 365, Active Directory, Network, and Desktop support
- **1,200 device records** with lifecycle and refresh tracking
- **3,000 Active Directory events** covering provisioning, access management, and automation metrics

The dashboard is designed to showcase the kind of operational analytics a Senior Service Desk Analyst would use to monitor performance, identify trends, and drive continuous improvement.

---

## Features

### Incident Analytics
- Weekly ticket volume trends with area charts
- Priority distribution breakdown
- Trade Floor vs Corporate support comparison
- Top incident subcategories (Bloomberg, Reuters, O365, VPN, etc.)
- Resolution time analysis by category (mean, median, P90)
- Contact method breakdown (walk-up, phone, email, self-service, Teams)
- VIP vs standard requester handling comparison

### SLA Compliance
- Monthly SLA compliance trend with 95% target line
- Compliance rates by priority level (Critical, High, Medium, Low)
- Compliance by incident category
- Location-based SLA performance with heat-mapped bars
- Detailed compliance tables with drill-down

### Device Lifecycle
- Device refresh status by type (Trading Workstations, Bloomberg Terminals, Laptops, etc.)
- Age distribution histogram
- Warranty coverage analysis
- Refresh cost forecasting with dollar estimates
- Full device inventory with filtering

### Active Directory User Analytics
- Monthly AD provisioning event volumes
- Automated vs manual action split
- Action type summary with success rates
- Department-level activity breakdown
- Failed action analysis
- Completion time comparison (automated vs manual) with box plots

---

## Architecture

```
it-service-desk-dashboard-poc/
|
|-- app.py                 # Streamlit dashboard (entry point)
|-- data_generator.py      # Synthetic data generation engine
|-- analytics.py           # Core analytics and KPI calculations
|-- requirements.txt       # Python dependencies
|-- .env.example           # Environment variable template
|-- .gitignore             # Git ignore rules
|-- README.md              # This file
```

### Data Flow

```
data_generator.py          analytics.py              app.py
+-----------------+       +-----------------+       +------------------+
| generate_tickets|  -->  | SLA compliance  |  -->  | Streamlit tabs   |
| generate_devices|  -->  | Resolution stats|  -->  | Plotly charts    |
| generate_ad_    |  -->  | Device lifecycle|  -->  | KPI metrics      |
|   events        |       | AD analytics    |       | Interactive      |
+-----------------+       +-----------------+       |   filters        |
                                                    +------------------+
```

- **data_generator.py** produces three DataFrames (tickets, devices, AD events) using the Faker library and domain-specific constants that model a financial services IT environment.
- **analytics.py** consumes raw DataFrames and returns aggregated, analysis-ready DataFrames covering SLA compliance, trend analysis, cost forecasting, and more.
- **app.py** orchestrates the Streamlit UI, calling analytics functions and rendering interactive Plotly visualisations.

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd it-service-desk-dashboard-poc

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

### Configuration

Copy the example environment file and adjust values as needed:

```bash
copy .env.example .env
```

---

## Technology Stack

| Component        | Technology        | Purpose                              |
|-----------------|-------------------|--------------------------------------|
| Dashboard       | Streamlit 1.40    | Interactive web application          |
| Visualisation   | Plotly 5.24       | Interactive charts and graphs        |
| Data Processing | Pandas 2.2        | Data manipulation and analysis       |
| Data Generation | Faker 30.8        | Realistic synthetic data             |
| Numerical       | NumPy 1.26        | Statistical distributions            |

---

## Screenshots

> After running the dashboard, screenshots can be captured for each tab:

| Tab | Description |
|-----|-------------|
| **Incident Analytics** | Weekly volumes, priority breakdown, trade floor vs corporate comparison |
| **SLA Compliance** | Monthly trends with target lines, compliance by priority and location |
| **Device Lifecycle** | Refresh tracking, age distribution, warranty coverage, cost forecast |
| **AD User Analytics** | Provisioning trends, automation rates, failure analysis |

---

## Key Technical Highlights

- **Modular architecture**: Data generation, analytics, and presentation layers are cleanly separated
- **Cached data loading**: Streamlit's `@st.cache_data` prevents redundant data regeneration
- **Interactive filtering**: Sidebar controls for date range, location, support type, and priority dynamically update all charts
- **Financial services domain modelling**: Incident categories include Bloomberg Terminal issues, FIX engine connectivity, trading platform problems, and multi-monitor setups
- **Statistical distributions**: Resolution times follow log-normal distributions; ticket creation times have business-hours bias
- **Comprehensive KPIs**: Top-level metrics with month-over-month change indicators

---

## License

This project is a proof-of-concept for demonstration purposes. All data is synthetically generated and does not represent any real organisation.
