# SD-QKD security lab

Academic Streamlit app for exploring simulated superdense quantum key distribution, authentication decisions, and QBER-based run history. No physical quantum channel is used.

## Run the app

From the project root, activate the virtual environment and start the Streamlit entry point:

```powershell
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

`app.py` handles routing, account access, and the signed-in navigation. It is the only file to run directly.

## Project layout

```text
app.py                         Streamlit entry point and route controller
pages/                         Front-end screens
  00_Landing.py                Public project overview
  01_Simulation.py             Live simulation controls and results
  02_Reports_Analytics.py      Saved run history, charts, and CSV export
frontend/                      Shared visual components and static front-end files
  quantum_background.py        Interactive Three.js particle backdrop
  assets/figma_landing/        Figma artwork and icons
  visuals/quantum_visuals.html Simulation result visualization
backend/                       Authentication, data, and quantum simulation logic
  database/                    Users, sessions, and experiment records
  security/                    Simulation controller and QBER decisions
  quantum/                     Circuit encoding and channel models
sd_qkd_results.db              Local SQLite data store
```

The public overview and account links stay in the same browser tab. Create an account, then use the sign-in link to continue to the simulation workspace.
