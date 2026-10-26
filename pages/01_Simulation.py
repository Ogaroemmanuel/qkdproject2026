from __future__ import annotations

import streamlit as st

from backend.database.db_manager import log_simulation
from backend.security.controller import run_simulation


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Research console / live experiment</div>
      <h1>Quantum key exchange</h1>
      <p>Set the channel conditions, run the experiment, then follow the exchange in the immersive lab view.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown("#### Experiment setup")
    with st.form("simulation_config_form"):
        left, middle, right = st.columns([0.9, 1.25, 1.1], gap="large", vertical_alignment="center")
        with left:
            key_size = st.selectbox("Key sequence", [8, 16, 32], index=1, format_func=lambda size: f"{size} bits")
        with middle:
            num_shots = st.slider("Measurement shots", min_value=128, max_value=4096, value=1024, step=128)
        with right:
            eve_active = st.toggle("Simulate an interception", value=False, help="Enables the configured Eve attack model in the simulator.")
            st.caption("Eve / man-in-the-middle")
        submitted = st.form_submit_button("Run experiment", type="primary", icon=":material/play_arrow:", width="stretch")

if submitted:
    try:
        with st.spinner("Preparing the quantum channel…"):
            result = run_simulation(key_size, eve_active, num_shots)
            log_simulation(
                key_size,
                num_shots,
                eve_active,
                result["qber_value"],
                result["threshold"],
                result["status"],
                result["kill_switch_triggered"],
            )
        st.session_state["last_simulation"] = {
            "key_size": key_size,
            "num_shots": num_shots,
            "eve_active": bool(eve_active),
            "result": result,
        }
        st.switch_page("pages/03_Quantum_Visualization.py")
    except Exception as exc:
        st.error(f"The experiment could not be completed: {exc}", icon=":material/error:")


saved = st.session_state.get("last_simulation")
if saved:
    result = saved["result"]
    qber = float(result["qber_value"])
    threshold = float(result["threshold"])
    killed = bool(result["kill_switch_triggered"])

    st.markdown("#### Latest result")
    metric_cols = st.columns(3)
    metric_cols[0].metric("QBER", f"{qber:.2f}%", delta=f"{qber - threshold:+.2f}% vs limit", delta_color="inverse")
    metric_cols[1].metric("Security decision", "Interrupted" if killed else "Accepted")
    metric_cols[2].metric("Interception", "Active" if saved["eve_active"] else "Inactive")

    if killed:
        st.error("The security controller interrupted this simulated session after evaluating the channel.", icon=":material/gpp_bad:")
    else:
        st.success("The security controller accepted this simulated session.", icon=":material/verified_user:")

    action, context = st.columns([1, 2], vertical_alignment="center")
    with action:
        if st.button("Replay in 3D", icon=":material/view_in_ar:", type="primary", width="stretch"):
            st.switch_page("pages/03_Quantum_Visualization.py")
    with context:
        st.caption(f"{saved['key_size']} bit sequence · {saved['num_shots']:,} measurement shots · decision limit {threshold:.2f}%")

    with st.expander("Inspect key outputs"):
        sent, received = st.columns(2, gap="large")
        with sent:
            st.caption("Alice · transmitted key")
            st.code(str(result.get("sent_key", "Not supplied by simulation")), language="text")
        with received:
            st.caption("Bob · received key")
            st.code(str(result.get("received_key", "Not supplied by simulation")), language="text")
else:
    st.caption("Choose the channel settings and run an experiment. The 3D lab opens automatically when the result is ready.")
