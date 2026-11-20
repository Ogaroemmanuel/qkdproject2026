from __future__ import annotations

import json
import base64
from pathlib import Path

import streamlit as st
from backend.quantum.state_trace import build_state_trace


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "frontend" / "visuals" / "quantum_visuals.html"


@st.cache_data
def hardware_model_data():
    model = ROOT / "frontend" / "assets" / "hardware" / "classic_laptop.glb"
    return "data:model/gltf-binary;base64," + base64.b64encode(model.read_bytes()).decode("ascii")

_VIEWER = st.components.v2.component(
    "sd_qkd_immersive_viewer",
    html='<div id="qkd-viewer-host"></div>',
    js="""
export default function (component) {
  const { parentElement, data, setTriggerValue } = component;
  const host = parentElement.querySelector("#qkd-viewer-host");
  if (!host || !data?.html) return;

  let frame = host.querySelector("iframe");
  if (!frame) {
    frame = document.createElement("iframe");
    frame.title = "Interactive 3D quantum channel visualization";
    frame.setAttribute("allow", "fullscreen");
    Object.assign(frame.style, {
      position: "fixed", top: "0", left: "50%", transform: "translateX(-50%)",
      width: "100vw", height: "100vh", border: "0", zIndex: "2147483000",
      background: "#050b13", margin: "0"
    });
    host.appendChild(frame);
  }

  if (frame.__qkdHtml !== data.html) {
    frame.__qkdHtml = data.html;
    frame.srcdoc = data.html;
  }

  const requestReturn = () => setTriggerValue("return_to_simulation", true);
  window.__sdQkdRequestReturn = requestReturn;
  return () => {
    if (window.__sdQkdRequestReturn === requestReturn) {
      delete window.__sdQkdRequestReturn;
    }
  };
}
""",
)

saved = st.session_state.get("last_simulation")
st.markdown(
    """
    <style>
      [data-testid="stSidebar"], [data-testid="stHeader"] { display: none !important; }
      [data-testid="stMain"] .block-container { max-width: none !important; padding: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

if saved:
    result = saved["result"]
    visual_config = {
        "eveActive": bool(saved["eve_active"]),
        "qberValue": float(result["qber_value"]),
        "threshold": float(result["threshold"]),
        "killSwitch": bool(result["kill_switch_triggered"]),
        "backendStatus": str(result.get("status", "Completed")),
        "keySize": int(saved["key_size"]),
        "shots": int(saved["num_shots"]),
        "sentMessage": str(result.get("sent_key", "")),
        "receivedMessage": str(result.get("received_key", "")),
        "firstPair": (result.get("pair_results") or [{}])[0],
        "errorBits": int(result.get("error_bits", 0)),
        "totalBits": int(result.get("total_bits", saved["key_size"] * saved["num_shots"])),
        "modelVersion": result.get("model_version", "superdense-bit-order-corrected-v2"),
        "noiseProbability": result.get("configuration", {}).get("noise_probability", 0),
        "confidenceInterval": result.get("confidence_interval"),
        "completedBatches": result.get("completed_batches"),
        "plannedBatches": result.get("planned_batches"),
        "untransmittedBits": result.get("untransmitted_bits", 0),
        "batchResults": result.get("batches", []),
        "previewMode": False,
    }
else:
    visual_config = {
        "eveActive": False,
        "qberValue": 0,
        "threshold": 11,
        "killSwitch": False,
        "backendStatus": "Interactive preview · run an experiment to show measured results",
        "keySize": 16,
        "shots": 1024,
        "sentMessage": "",
        "receivedMessage": "",
        "firstPair": {},
        "errorBits": 0,
        "totalBits": 0,
        "modelVersion": "preview",
        "previewMode": True,
    }

try:
    # Older saved runs can still replay the exact first-pair state progression.
    first_pair = dict(visual_config["firstPair"])
    visual_config["firstPair"] = first_pair
    if not first_pair.get("state_trace"):
        first_pair["state_trace"] = build_state_trace(first_pair.get("sent_bits", "00"), visual_config["eveActive"], visual_config.get("noiseProbability", 0))
    visual_config["hardwareModel"] = hardware_model_data()
    html_content = HTML_PATH.read_text(encoding="utf-8").replace(
        "__QUANTUM_EXPLAINER__", (HTML_PATH.parent / "quantum_explainer.js").read_text(encoding="utf-8")
    )
    if "__CONFIG_JSON__" not in html_content:
        st.error("The 3D scene is missing its configuration marker.")
    else:
        safe_json = json.dumps(visual_config).replace("</", "<\\/")
        html_content = html_content.replace("__CONFIG_JSON__", safe_json)
        viewer = _VIEWER(
            data={"html": html_content},
            key=f"qkd_immersive_viewer_{st.session_state.get('visualization_visit', 0)}",
            width="stretch",
            height=900,
            on_return_to_simulation_change=lambda: None,
        )
        if viewer.return_to_simulation:
            # An exit trigger must never survive into a later viewer visit.
            st.session_state["visualization_visit"] = st.session_state.get("visualization_visit", 0) + 1
            st.switch_page("pages/01_Simulation.py")
except FileNotFoundError:
    st.error("A required scene or hardware asset is missing. Restore frontend/visuals and frontend/assets/hardware.")
