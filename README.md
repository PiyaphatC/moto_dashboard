# 🛵 Bangkok Motorcycle Taxi Survey Dashboard

An interactive data dashboard for the **Bangkok Living Lab** pilot survey on informal motorcycle taxi (*Win*) and app-based motorcycle taxi usage.

Built as part of the **CUTI × Columbia ISM** research collaboration.

---

## Overview

This dashboard visualizes pilot survey results collected in March 2025, covering:

- **Demand side** — passengers of Win stands and app-based services
- **Supply side** — Win drivers and app-based drivers

Key topics include trip behavior, EV adoption attitudes, demographics, and driver profiles.

---

## Dashboard Sections

| Section | Description |
|---|---|
| Overview | Response counts, interactive map of survey locations |
| Demand — Usage & Behavior | Trip purpose, fare, distance, payment, Win vs App comparison |
| Demand — EV Attitudes | Willingness to use/pay for EV taxis, perceived pros & cons |
| Demand — Demographics | Age, gender, education, income |
| Supply — Driver Profile | Driver demographics, income, EV interest, problems faced |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the dashboard locally

```bash
streamlit run dashboard.py
```

### 3. Run with public URL (via Cloudflare Tunnel)

```bash
bash start.sh
```

This starts Streamlit on port 8501 and exposes it publicly via a Cloudflare Tunnel URL (no account required).

---

## Auto-update

The dashboard reads the source Excel file every **30 seconds**. When the file is updated (e.g., via OneDrive sync), the dashboard reflects changes automatically — no restart needed.

---

## Data

The source data file is **not included** in this repository (it lives in a shared OneDrive folder). Update the `DATA_FILE` path in `dashboard.py` to point to your local copy.

```
Data_Pilot_Submitted.xlsx
├── Demand_Win     — Win passengers (n=22)
├── Demand_Rider   — App passengers (n=20)
├── Supply_Win     — Win drivers (n=47)
└── Supply_Rider   — App drivers (n=15)
```

---

## Project

**Columbia ISM Bangkok Living Lab**  
Supply and Demand Survey — Informal Transport & Shared Mobility  
Chulalongkorn University Transport Institute (CUTI)
