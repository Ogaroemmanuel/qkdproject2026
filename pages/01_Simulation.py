from __future__ import annotations

import streamlit as st

from backend.database.db_manager import log_simulation
from backend.security.controller import run_simulation


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Research console / live experiment</div>
        <h1>Superdense-coding experiment</h1>
      <p>Configure the two-qubit circuit and replay its encoded message, modeled channel interception, Bob’s decode, and error-rate decision.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown("#### Experiment setup")
    with st.form("simulation_config_form"):
        left, middle, right = st.columns([0.9, 1.25, 1.1], gap="large", vertical_alignment="center")
        with left:
            key_size = st.selectbox("Message length", [8, 16, 32], index=1, format_func=lambda size: f"{size} bits")
        with middle:
            num_shots = st.slider("Trials per batch", min_value=128, max_value=4096, value=1024, step=128)
        with right:
            eve_active = st.toggle("Simulate an interception", value=False, help="Enables the configured Eve attack model in the simulator.")
            st.caption("Eve / Z-basis measurement")
        with st.expander("Channel and decision settings"):
            noise = st.slider("Pauli channel error probability (%)", 0, 30, 2,
                              help="Probability of applying X, Y, or Z to the traveling qubit; this is not the measured bit-error rate.")
            test_percent = st.slider("Trials reserved for independent test probes (%)", 10, 80, 50,
                                     help="Probe messages are independent of payload bits. Both probe bits are disclosed and excluded from retained candidates.")
            limit = st.slider("Application error limit (%)", 1, 30, 11)
            random_seed = st.checkbox("Randomize experiment seed", value=True)
            seed_value = st.number_input("Reproducible seed", min_value=0, max_value=4294967295, value=42)
            st.caption("A 95% simultaneous Hoeffding interval accounts for every planned batch check. This is a disturbance test, not a QKD security bound.")
        submitted = st.form_submit_button("Run experiment", type="primary", icon=":material/play_arrow:", width="stretch")

if submitted:
    try:
        with st.spinner("Preparing the quantum channel…"):
            result = run_simulation(key_size, eve_active, num_shots,
                                    noise_probability=noise/100, test_fraction=test_percent/100,
                                    error_limit=limit/100, seed=None if random_seed else int(seed_value))
            run_id = log_simulation(
                key_size,
                num_shots,
                eve_active,
                result["qber_value"],
                result["threshold"],
                result["status"],
                result["kill_switch_triggered"],
                model_version=result["model_version"], result=result,
            )
        st.session_state["last_simulation"] = {
            "key_size": key_size,
            "num_shots": num_shots,
            "eve_active": bool(eve_active),
            "result": result,
            "run_id": run_id,
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
    status = result.get("status", "Within limit")
    metric_cols[0].metric("Disclosed test-bit errors", f"{qber:.2f}%", help="Estimated from disclosed test shots only. These shots are discarded from retained candidates.")
    metric_cols[1].metric("Decision", status)
    metric_cols[2].metric("Completed batches", f"{result.get('completed_batches', saved['key_size']//2)} / {result.get('planned_batches', saved['key_size']//2)}")
    if result.get("confidence_interval"):
        low, high = result["confidence_interval"]
        st.caption(f"95% simultaneous error interval: {low:.2f}%–{high:.2f}% · application limit {threshold:.2f}% · seed {result['seed']}")
    if killed:
        st.error(f"Rejected after {result.get('completed_batches', 0)} batch(es). {result.get('untransmitted_bits', 0)} planned message bits were not transmitted. No retained candidates are released.")
    elif status == "Inconclusive":
        st.warning("The interval crosses the application limit. Candidates remain withheld; increase shots or the test fraction to reduce uncertainty.")
    else:
        st.success("The full experiment completed with the upper confidence bound within the application limit. This is not a cryptographic security guarantee.")

    action, context = st.columns([1, 2], vertical_alignment="center")
    with action:
        if st.button("Replay in 3D", icon=":material/view_in_ar:", type="primary", width="stretch"):
            st.switch_page("pages/03_Quantum_Visualization.py")
    with context:
        st.caption(f"{saved['key_size']} message bits · {saved['num_shots']:,} trials per batch, including independent probes · decision limit {threshold:.2f}%")

    with st.expander("Inspect transmitted message examples"):
        sent, received = st.columns(2, gap="large")
        with sent:
            st.caption("Alice · encoded message")
            st.code(str(result.get("sent_key", "Not supplied by simulation")), language="text")
        with received:
            st.caption("Bob · one sampled decoded message")
            st.code(str(result.get("received_key", "Not supplied by simulation")), language="text")
else:
    st.caption("This educational superdense-coding simulation is not a complete quantum key-distribution protocol or a physical network. The 3D lab opens when a run finishes.")
