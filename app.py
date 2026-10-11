import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
from security.controller import run_simulation
from database.db_manager import (
    init_db, log_simulation, fetch_logs, register_user, 
    authenticate_user, create_session, verify_session, destroy_session
)

init_db()
st.set_page_config(page_title="SD-QKD Simulation", layout="wide")

current_token = st.query_params.get("session")
active_user = None

if current_token:
    active_user = verify_session(current_token, max_idle_minutes=15)
    if not active_user:
        st.error("Session expired due to inactivity. Please log in again.")
        del st.query_params["session"]
        time.sleep(2)
        st.rerun()

if not active_user:
    st.title("🔐 SD-QKD System Access")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Researcher Login")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if authenticate_user(login_user, login_pass):
                new_token = create_session(login_user)
                st.query_params["session"] = new_token
                st.rerun()
            else:
                st.error("Invalid username or password.")
                
    with tab2:
        st.subheader("Register New Researcher")
        reg_user = st.text_input("New Username")
        reg_pass = st.text_input("New Password", type="password")
        if st.button("Register"):
            if reg_user and reg_pass:
                if register_user(reg_user, reg_pass):
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error("Username already exists.")
            else:
                st.warning("Please fill in both fields.")

else:
    st.sidebar.success(f"Logged in as: {active_user}")
    if st.sidebar.button("Logout"):
        destroy_session(current_token)
        del st.query_params["session"]
        st.rerun()

    st.title("Superdense QKD Web Authentication Simulator")
    
    st.sidebar.header("Configuration Parameters")
    key_size = st.sidebar.selectbox("Key Sequence Size", [8, 16, 32], index=1)
    num_shots = st.sidebar.slider("Simulation Shots", min_value=128, max_value=4096, value=1024, step=128)
    eve_active = st.sidebar.toggle("Activate MITM Eavesdropper (Eve)", value=False)

    if st.sidebar.button("Start Simulation"):
        st.subheader("📡 Live Quantum Network Simulation")
        
        try:
            with open("quantum_visuals.html", "r", encoding="utf-8") as f:
                html_content = f.read()
            js_boolean = "true" if eve_active else "false"
            html_content = html_content.replace("REPLACE_ME_EVE_ACTIVE", js_boolean)
            components.html(html_content, height=400)
        except FileNotFoundError:
            st.error("⚠️ quantum_visuals.html file not found.")

        st.divider()
        st.markdown("### 📦 Packet Interception Feed")
        log_window = st.empty()
        
        if eve_active:
            log_window.warning("⏳ [CLASSICAL LAYER] Alice sending RSA ClientHello packet...")
            time.sleep(1.5)
            log_window.error("🚨 [CLASSICAL LAYER] Eve intercepted ClientHello! Forwarding spoofed packet to Bob...")
            time.sleep(1.5)
            log_window.warning("⏳ [CLASSICAL LAYER] Bob sending ServerHello & Certificate...")
            time.sleep(1.5)
            log_window.error("🚨 [CLASSICAL LAYER] Eve intercepts and swaps in a forged RSA certificate! Alice accepts it.")
            time.sleep(2)
            log_window.info("🛡️ [QUANTUM LAYER] Classical handshake compromised. Initiating SD-QKD Key Exchange...")
            time.sleep(1.5)
            log_window.warning("⏳ [QUANTUM LAYER] Alice sending entangled Bell states (Qubits)...")
            time.sleep(1.5)
            log_window.error("💥 [QUANTUM LAYER] Eve attempts to measure/steal Qubits in transit!")
            time.sleep(1)
            log_window.error("💥 [QUANTUM LAYER] Physics enforcement: Eve's observation collapsed the quantum state. Key corrupted.")
            time.sleep(1.5)
        else:
            log_window.success("⏳ [CLASSICAL LAYER] Exchanging Hello packets and validating certificates...")
            time.sleep(2)
            log_window.success("✅ [CLASSICAL LAYER] Certificates validated. No MITM detected.")
            time.sleep(1)
            log_window.info("🛡️ [QUANTUM LAYER] Initiating SD-QKD Key Exchange...")
            time.sleep(1.5)
            log_window.success("⏳ [QUANTUM LAYER] Alice sending entangled Bell states (Qubits)...")
            time.sleep(1.5)

        result = run_simulation(key_size, eve_active, num_shots)
        log_simulation(key_size, num_shots, eve_active, result["qber_value"], result["threshold"], result["status"], result["kill_switch_triggered"])
        
        if eve_active:
            log_window.error("📉 [QUANTUM LAYER] Corrupted key received by Bob. Running QBER diagnostic...")
        else:
            log_window.success("✅ [QUANTUM LAYER] Key received by Bob. Running QBER diagnostic...")
            
        time.sleep(1.5)
        
        st.subheader("Real-Time Telemetry Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Transmitted Key (Alice)", result["sent_key"])
        
        if eve_active:
            col2.error(f"Received Key (Bob) - CORRUPTED\n\n{result['received_key']}")
        else:
            col2.metric("Received Key (Bob)", result["received_key"])
            
        delta_color = "inverse" if result["kill_switch_triggered"] else "normal"
        col3.metric(
            "Measured QBER", 
            f"{result['qber_value']}%", 
            delta=f"{result['qber_value'] - result['threshold']:.2f}% vs Threshold", 
            delta_color=delta_color
        )
        
        if result["kill_switch_triggered"]:
            st.error(f"🚨 **KILL-SWITCH ACTIVATED**: Attack detected in physical layer. QBER exceeds {result['threshold']}% tolerance. Session terminated before user data transmission.")
        else:
            st.success(f"✅ **HANDSHAKE SECURED**: QBER within safe tolerance. Symmetrical keys established.")

    st.divider()
    st.subheader("Historical Simulation Logs")
    logs = fetch_logs()
    if logs:
        df = pd.DataFrame(logs, columns=["Run ID", "Timestamp", "Key Size", "Shots", "Eve Active", "QBER (%)", "Threshold (%)", "Status", "Kill-Switch"])
        st.dataframe(df, use_container_width=True)