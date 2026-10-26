import pandas as pd
import streamlit as st
from backend.database.db_manager import fetch_logs

COLUMNS = [
    "Run ID", "Timestamp", "Key Size", "Shots", "Eve Active",
    "QBER (%)", "Threshold (%)", "Status", "Kill-Switch"
]

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Experiment history and evaluation</div>
      <h1>Reports & Analytics</h1>
      <p>A dedicated page for reviewing simulation history, comparing QBER with the configured threshold, measuring kill-switch outcomes, and exporting research records.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(ttl=10, show_spinner=False)
def load_log_data():
    rows = fetch_logs()
    if not rows:
        return pd.DataFrame(columns=COLUMNS)
    if isinstance(rows, pd.DataFrame):
        df = rows.copy()
        if len(df.columns) == len(COLUMNS):
            df.columns = COLUMNS
        return df
    return pd.DataFrame(rows, columns=COLUMNS)

def to_flag(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"1", "true", "yes", "enabled", "on"})

df = load_log_data()
if df.empty:
    st.info("No simulation records have been saved yet. Run an experiment from **Live Simulation** and return here to view its report.")
    st.stop()

df["QBER (%)"] = pd.to_numeric(df["QBER (%)"], errors="coerce")
df["Threshold (%)"] = pd.to_numeric(df["Threshold (%)"], errors="coerce")
df["Key Size"] = pd.to_numeric(df["Key Size"], errors="coerce")
df["Shots"] = pd.to_numeric(df["Shots"], errors="coerce")
df["Eve Active"] = to_flag(df["Eve Active"])
df["Kill-Switch"] = to_flag(df["Kill-Switch"])
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
df["Run ID"] = df["Run ID"].astype(str)
df["QBER > threshold"] = df["QBER (%)"] > df["Threshold (%)"]

st.markdown("### Filter the report")
f1, f2, f3 = st.columns([1, 1, 1.4], gap="medium")
with f1:
    key_options = sorted([int(x) for x in df["Key Size"].dropna().unique()])
    chosen_keys = st.multiselect("Key size", key_options, default=key_options)
with f2:
    attack_filter = st.selectbox("Eve scenario", ["All runs", "Eve enabled", "Eve disabled"])
with f3:
    search_text = st.text_input("Search status", placeholder="e.g. accepted, terminated")

filtered = df.copy()
if chosen_keys:
    filtered = filtered[filtered["Key Size"].isin(chosen_keys)]
if attack_filter == "Eve enabled":
    filtered = filtered[filtered["Eve Active"]]
elif attack_filter == "Eve disabled":
    filtered = filtered[~filtered["Eve Active"]]
if search_text.strip():
    filtered = filtered[filtered["Status"].astype(str).str.contains(search_text.strip(), case=False, na=False)]

total_runs = len(filtered)
attack_runs = int(filtered["Eve Active"].sum()) if total_runs else 0
kill_runs = int(filtered["Kill-Switch"].sum()) if total_runs else 0
avg_qber = filtered["QBER (%)"].mean() if total_runs else float("nan")
max_qber = filtered["QBER (%)"].max() if total_runs else float("nan")

st.markdown("### Security overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total runs", f"{total_runs:,}")
m2.metric("Eve-enabled runs", f"{attack_runs:,}")
m3.metric("Kill-switch activations", f"{kill_runs:,}")
m4.metric("Average QBER", f"{avg_qber:.2f}%" if pd.notna(avg_qber) else "—")

m5, m6, m7 = st.columns(3)
m5.metric("Highest measured QBER", f"{max_qber:.2f}%" if pd.notna(max_qber) else "—")
m6.metric("Threshold exceedances", f"{int(filtered['QBER > threshold'].sum()):,}" if total_runs else "0")
accept_rate = ((total_runs - kill_runs) / total_runs * 100) if total_runs else 0
m7.metric("Sessions not terminated", f"{accept_rate:.1f}%" if total_runs else "—")

st.markdown("### QBER trend and attack comparison")
chart_left, chart_right = st.columns(2, gap="large")
with chart_left:
    with st.container(border=True):
        st.markdown("**Measured QBER vs configured threshold**")
        chart_df = filtered.dropna(subset=["QBER (%)", "Threshold (%)"]).copy()
        if not chart_df.empty:
            chart_df["Run label"] = chart_df["Run ID"]
            chart_df = chart_df.set_index("Run label")[["QBER (%)", "Threshold (%)"]]
            st.line_chart(chart_df, height=300, color=["#74f5ff", "#ae8cff"])
        else:
            st.caption("No numeric QBER results are available for the selected filters.")
with chart_right:
    with st.container(border=True):
        st.markdown("**Average QBER by scenario**")
        if total_runs:
            scenario = filtered.assign(Scenario=filtered["Eve Active"].map({True: "Eve enabled", False: "Eve disabled"}))
            grouped = scenario.groupby("Scenario")["QBER (%)"].mean().dropna()
            if not grouped.empty:
                st.bar_chart(grouped, height=300, color="#74f5ff")
            else:
                st.caption("No QBER values are available for comparison.")
        else:
            st.caption("No runs match the selected filters.")

st.markdown("### Run history")
if filtered.empty:
    st.info("No records match the selected filters.")
else:
    display_df = filtered.copy()
    display_df["Eve Active"] = display_df["Eve Active"].map({True: "Enabled", False: "Disabled"})
    display_df["Kill-Switch"] = display_df["Kill-Switch"].map({True: "Triggered", False: "Not triggered"})
    display_df["QBER > threshold"] = display_df["QBER > threshold"].map({True: "Yes", False: "No"})
    display_df["Timestamp"] = display_df["Timestamp"].astype(str).replace("NaT", "Unknown")
    preferred = COLUMNS + ["QBER > threshold"]
    display_df = display_df[[col for col in preferred if col in display_df.columns]]
    st.dataframe(display_df, width="stretch", hide_index=True)

    csv_data = display_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇ Export filtered report (CSV)",
        data=csv_data,
        file_name="sd_qkd_simulation_report.csv",
        mime="text/csv",
        type="primary",
    )
