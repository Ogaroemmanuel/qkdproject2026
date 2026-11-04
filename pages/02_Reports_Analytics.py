"""Run history and outcome summaries from saved software simulations."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.database.db_manager import fetch_logs


COLUMNS = [
    "Run ID", "Timestamp", "Message length", "Shots", "Interception",
    "Decoded bit error (%)", "Error limit (%)", "Controller result", "Kill switch", "Model version",
]
CORRECTED_MODEL = "superdense-bit-order-corrected-v2"
LEGACY_MODEL = "legacy-before-bit-order-fix"


@st.cache_data(ttl=10, show_spinner=False)
def load_log_data() -> pd.DataFrame:
    rows = fetch_logs()
    if not rows:
        return pd.DataFrame(columns=COLUMNS)
    if isinstance(rows, pd.DataFrame):
        frame = rows.copy()
        if len(frame.columns) == len(COLUMNS):
            frame.columns = COLUMNS
        return frame
    # fetch_logs returns the SQLite table's run_id-first tuple shape.
    return pd.DataFrame(rows, columns=COLUMNS)


def to_flag(values: pd.Series) -> pd.Series:
    return values.astype(str).str.strip().str.lower().isin({"1", "true", "yes", "enabled", "on"})


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Saved simulations / measured outcomes</div>
      <h1>Simulation reports</h1>
      <p>Review decoded-message error rates, configured limits, interception settings, and controller outcomes for each saved superdense-coding run.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

df = load_log_data()
if df.empty:
    st.info("No simulation runs have been saved yet. Run an experiment to build your report history.", icon=":material/monitoring:")
    st.caption("These reports describe the software simulation. They are not measurements from a physical quantum network.")
    st.stop()

for column in ("Decoded bit error (%)", "Error limit (%)", "Message length", "Shots"):
    df[column] = pd.to_numeric(df[column], errors="coerce")
df["Interception"] = to_flag(df["Interception"])
df["Kill switch"] = to_flag(df["Kill switch"])
df["Controller result"] = df["Kill switch"].map({True: "Interrupted", False: "Within limit"})
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
df["Run ID"] = df["Run ID"].astype(str)
if "Model version" not in df:
    df["Model version"] = LEGACY_MODEL
df["Error above limit"] = df["Decoded bit error (%)"] > df["Error limit (%)"]

with st.container(border=True):
    st.markdown("#### Filter runs")
    filter_cols = st.columns([1.0, 1.0, 1.0, 1.15, 1.35], gap="medium")
    with filter_cols[0]:
        keys = sorted(int(value) for value in df["Message length"].dropna().unique())
        chosen_keys = st.multiselect("Message length", keys, default=keys)
    with filter_cols[1]:
        eve_filter = st.selectbox("Interception", ["All runs", "Eve enabled", "Eve disabled"])
    with filter_cols[2]:
        decision_filter = st.selectbox("Controller outcome", ["All outcomes", "Within limit", "Interrupted"])
    with filter_cols[3]:
        search = st.text_input("Find run ID", placeholder="Search saved run IDs")
    with filter_cols[4]:
        result_version = st.selectbox("Calculation version", ["Corrected runs only", "All versions", "Legacy runs only"])

filtered = df.copy()
filtered = filtered[filtered["Message length"].isin(chosen_keys)]
if eve_filter == "Eve enabled":
    filtered = filtered[filtered["Interception"]]
elif eve_filter == "Eve disabled":
    filtered = filtered[~filtered["Interception"]]
if decision_filter != "All outcomes":
    filtered = filtered[filtered["Controller result"] == decision_filter]
if search.strip():
    filtered = filtered[filtered["Run ID"].str.contains(search.strip(), case=False, na=False)]
if result_version == "Corrected runs only":
    filtered = filtered[filtered["Model version"] == CORRECTED_MODEL]
elif result_version == "Legacy runs only":
    filtered = filtered[filtered["Model version"] != CORRECTED_MODEL]

legacy_count = int((df["Model version"] != CORRECTED_MODEL).sum())
if legacy_count and result_version == "All versions":
    st.warning(
        f"{legacy_count:,} older run(s) predate the Qiskit bit-order correction. Their recorded error rates may be wrong; use the calculation-version filter to exclude them from comparisons."
    )

run_count = len(filtered)
error_values = filtered["Decoded bit error (%)"].dropna()
mean_error = error_values.mean() if not error_values.empty else None
exceed_count = int(filtered["Error above limit"].sum())
blocked_count = int(filtered["Kill switch"].sum())
eve_count = int(filtered["Interception"].sum())

st.markdown("### Outcome overview")
with st.container(horizontal=True, gap="small"):
    st.metric("Runs in view", f"{run_count:,}", border=True)
    st.metric("Mean decoded bit error", f"{mean_error:.2f}%" if mean_error is not None else "—", border=True)
    st.metric("Runs above configured limit", f"{exceed_count:,}", border=True)
    st.metric("Controller interruptions", f"{blocked_count:,}", border=True)

st.caption(f"The simplified Eve measurement was enabled in {eve_count:,} of {run_count:,} displayed run(s). This group comparison is descriptive, not a real-world security guarantee.")

chart_left, chart_right = st.columns(2, gap="large")
with chart_left:
    with st.container(border=True):
        st.markdown("#### Decoded bit error and configured limit")
        chart_data = filtered.dropna(subset=["Decoded bit error (%)", "Error limit (%)"]).sort_values("Timestamp", na_position="last").copy()
        if chart_data.empty:
            st.caption("No numeric error rates are available for these filters.")
        else:
            chart_data["Run"] = chart_data["Run ID"]
            chart_data = chart_data.set_index("Run")[["Decoded bit error (%)", "Error limit (%)"]]
            st.line_chart(chart_data, height=285, color=["#74f5ff", "#ae8cff"], alt="Recorded decoded-message bit error and configured limit by run")
            st.caption("Each point is a saved run. The limit is the value used by that run’s controller decision.")

with chart_right:
    with st.container(border=True):
        st.markdown("#### Decoded bit error by interception setting")
        scenario = filtered.dropna(subset=["Decoded bit error (%)"]).copy()
        if scenario.empty:
            st.caption("No error-rate values are available for these filters.")
        else:
            scenario["Scenario"] = scenario["Interception"].map({True: "Eve enabled", False: "Eve disabled"})
            summary = scenario.groupby("Scenario", sort=False)["Decoded bit error (%)"].agg(["mean", "median", "count"])
            summary = summary.rename(columns={"mean": "Mean decoded error (%)", "median": "Median decoded error (%)", "count": "Runs"})
            st.bar_chart(summary[["Mean decoded error (%)"]], height=225, color="#74f5ff", alt="Mean decoded-message bit error for runs with Eve enabled versus disabled")
            st.dataframe(summary, hide_index=False, width="stretch", alt="Mean and median decoded-message bit error and run count by interception setting")
            if summary.index.nunique() < 2:
                st.caption("Both interception settings need saved runs for a side-by-side comparison.")

st.markdown("### Run history")
if filtered.empty:
    st.info("No saved runs match the selected filters.")
else:
    display = filtered.copy()
    display["Interception"] = display["Interception"].map({True: "Enabled", False: "Disabled"})
    display["Kill switch"] = display["Kill switch"].map({True: "Triggered", False: "Not triggered"})
    display["Error above limit"] = display["Error above limit"].map({True: "Yes", False: "No"})
    display["Timestamp"] = display["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").fillna("Unknown")
    display = display[[*COLUMNS, "Error above limit"]]
    st.dataframe(display, hide_index=True, width="stretch", alt="Filtered saved simulation runs with decoded bit error, limit, and controller outcome")
    st.download_button(
        "Export filtered runs (CSV)",
        data=display.to_csv(index=False).encode("utf-8-sig"),
        file_name="sd_qkd_simulation_report.csv",
        mime="text/csv",
        type="primary",
        icon=":material/download:",
    )

with st.expander("How to read this report"):
    st.markdown(
        "- **Decoded-message bit error rate** is the percentage of message bits Bob decoded differently from Alice across all simulator shots. It is QBER-like telemetry, not the sifted-key QBER of a complete BB84/DI-QKD protocol.\n"
        "- **Decision limit** is the configured threshold recorded with that run.\n"
        "- **Controller interruption** records whether the software kill-switch stopped the session.\n"
        "- **Eve enabled** marks runs where the simulator’s interception operation was turned on. The chart compares these groups but does not claim every attacked run must have higher QBER.\n"
        "- The implementation uses a software superdense-coding circuit and simplified channel model. Its outcomes are educational simulation results, not evidence of security in a deployed QKD system.\n"
        "- Legacy runs were created before Qiskit measurement bit strings were normalized into Alice’s message order. Rerun those experiments to get comparable corrected results."
    )
