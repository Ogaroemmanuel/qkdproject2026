from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "frontend" / "visuals" / "quantum_visuals.html"

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
        "previewMode": True,
    }

try:
    html_content = HTML_PATH.read_text(encoding="utf-8")
    if "__CONFIG_JSON__" not in html_content:
        st.error("The 3D scene is missing its configuration marker.")
    else:
        safe_json = json.dumps(visual_config).replace("</", "<\\/")
        html_content = html_content.replace("__CONFIG_JSON__", safe_json)
        viewer = _VIEWER(
            data={"html": html_content},
            key="qkd_immersive_viewer",
            width="stretch",
            height=900,
            on_return_to_simulation_change=lambda: None,
        )
        if viewer.return_to_simulation:
            st.switch_page("pages/01_Simulation.py")
except FileNotFoundError:
    st.error("The Three.js scene is missing from frontend/visuals.")
