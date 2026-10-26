"""Public landing page based on the SD-QKD Figma design."""

import base64
from pathlib import Path

import streamlit as st
from frontend.quantum_background import render_quantum_background


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = PROJECT_ROOT / "frontend" / "assets" / "figma_landing"


def _asset_uri(filename: str, media_type: str) -> str:
    payload = base64.b64encode((ASSET_DIR / filename).read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{payload}"


def render_landing_page() -> None:
    """Render the public project landing page and account entry links."""
    render_quantum_background()
    entangled = _asset_uri("entangled-particles.png", "image/png")
    wave_field = _asset_uri("quantum-wave-field.png", "image/png")
    icons = {
        name: _asset_uri(filename, "image/svg+xml")
        for name, filename in {
            "atom": "atom.svg",
            "arrow_up": "arrow-up-right.svg",
            "arrow_down": "arrow-down.svg",
            "activity": "activity.svg",
            "network": "network.svg",
            "analytics": "analytics.svg",
            "arrow_right": "arrow-right.svg",
            "binary": "binary.svg",
            "scan_eye": "scan-eye.svg",
            "scan_line": "scan-line.svg",
            "branch": "git-branch.svg",
        }.items()
    }
    icon = lambda key, alt="": f'<img class="icon" src="{icons[key]}" alt="{alt}">'

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');
        :root {{ --ink:#03050d; --panel:#0b1020; --panel-soft:#121a2d; --line:#293247; --white:#f3f7ff; --muted:#b0bccd; --cyan:#74f5ff; --violet:#ae8cff; }}
        html {{ scroll-behavior:smooth; }}
        [data-testid="stAppViewContainer"] {{ background:var(--ink)!important; color:var(--white)!important; }}
        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"], footer, #MainMenu {{ display:none!important; }}
        .block-container {{ max-width:1200px!important; padding:0!important; }}
        [data-testid="stMainBlockContainer"] {{ padding-top:0!important; padding-bottom:0!important; }}
        .stApp {{ background:var(--ink)!important; }}
        .landing {{ width:100%; overflow:hidden; background:var(--ink); color:var(--white); font-family:Inter,Arial,sans-serif; font-size:15px; line-height:1.6; }}
        .landing * {{ box-sizing:border-box; }}
        .landing h1, .landing h2, .landing h3 {{ font-family:Inter,Arial,sans-serif!important; color:var(--white)!important; }}
        .landing img.icon {{ display:block; object-fit:contain; }}
        .landing a {{ color:inherit; text-decoration:none; }}
        .landing a:hover {{ opacity:.82; }}
        .mono {{ font-family:'IBM Plex Mono',monospace; letter-spacing:.015em; }}
        .eyebrow {{ color:var(--cyan); font:400 11px/1.5 'IBM Plex Mono',monospace; letter-spacing:.04em; }}
        .muted {{ color:var(--muted); }}
        .site-nav {{ min-height:96px; padding:18px 48px; display:flex; align-items:center; justify-content:space-between; gap:24px; border-bottom:1px solid var(--line); }}
        .brand {{ display:flex; align-items:center; gap:12px; min-width:160px; }}
        .brand img {{ width:32px; height:32px; }}
        .brand-name {{ display:flex; flex-direction:column; line-height:1.15; }}
        .brand-name strong {{ font-size:19px; font-weight:700; }}
        .brand-name small {{ margin-top:4px; color:var(--muted); font:400 9px 'IBM Plex Mono',monospace; letter-spacing:.05em; }}
        .nav-links, .account-links {{ display:flex; align-items:center; gap:26px; font-size:14px; font-weight:500; white-space:nowrap; }}
        .account-links {{ gap:24px; }}
        .button {{ min-height:54px; padding:0 22px; display:inline-flex; align-items:center; justify-content:center; gap:14px; border:1px solid var(--line); border-radius:6px; font-size:14px; font-weight:600; white-space:nowrap; }}
        .button img {{ width:16px; height:16px; }}
        .button-primary {{ background:var(--cyan); border-color:var(--cyan); color:#041116!important; }}
        .button-dark {{ background:#041116; border-color:#041116; color:var(--cyan)!important; }}
        .hero {{ min-height:811px; padding:96px 48px 56px; position:relative; isolation:isolate; background-image:linear-gradient(90deg,rgba(3,5,13,.97) 0%,rgba(3,5,13,.92) 36%,rgba(3,5,13,.02) 100%),url('{entangled}'); background-position:center top; background-size:cover; }}
        .hero:after {{ content:''; position:absolute; inset:0; z-index:-1; background:linear-gradient(180deg,transparent 55%,rgba(3,5,13,.46)); pointer-events:none; }}
        .hero h1 {{ max-width:810px; margin:28px 0 25px; color:var(--white); font-size:clamp(54px,7.6vw,91px); font-weight:500; line-height:1.01; letter-spacing:-.045em; }}
        .hero-copy {{ max-width:540px; color:var(--muted); font-size:17px; line-height:1.65; }}
        .hero-actions {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:24px; }}
        .hero-audience {{ margin:20px 0 0; color:var(--muted); font-size:12px; }}
        .hero-caption {{ position:absolute; bottom:32px; left:48px; right:48px; display:flex; justify-content:space-between; gap:16px; color:var(--muted); font:400 10px 'IBM Plex Mono',monospace; letter-spacing:.03em; }}
        .hero-caption span:last-child {{ color:var(--cyan); }}
        .possibilities {{ padding:32px 48px; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:48px; border-top:1px solid var(--line); border-bottom:1px solid var(--line); }}
        .possibilities p {{ margin:8px 0 0; color:var(--white); font-size:18px; }}
        .section {{ padding:112px 48px; }}
        .section-heading {{ margin:0; color:var(--white); font-size:58px; font-weight:500; line-height:1.04; letter-spacing:-.035em; }}
        .workspace-intro {{ display:grid; grid-template-columns:1fr 350px; gap:80px; align-items:end; margin-bottom:52px; }}
        .workspace-intro .eyebrow {{ margin-bottom:20px; }}
        .workspace-intro p {{ margin:0; color:var(--muted); font-size:17px; line-height:1.65; }}
        .preview-window {{ overflow:hidden; border:1px solid #4b4a48; border-radius:14px; background:#1f1f1f; box-shadow:0 24px 50px rgba(0,0,0,.28); }}
        .window-bar {{ height:31px; padding:0 9px; display:flex; align-items:center; gap:8px; background:#202020; color:#fff; font-size:11px; }}
        .window-dot {{ width:12px; height:12px; border-radius:50%; background:#ff5f57; }}
        .window-dot:nth-child(2) {{ background:#ffbd2e; }} .window-dot:nth-child(3) {{ background:#28c840; }}
        .window-title {{ margin-left:12px; font-weight:600; }}
        .preview-body {{ padding:32px 30px; background:#0b1020; }}
        .preview-body .eyebrow {{ font-size:9px; }}
        .preview-body h3 {{ margin:4px 0 18px; color:var(--white); font-size:27px; font-weight:500; }}
        .preview-tabs {{ display:flex; gap:28px; padding-bottom:12px; border-bottom:1px solid var(--line); color:var(--muted); font-size:12px; }}
        .preview-tabs span:first-child {{ color:var(--cyan); }}
        .preview-fields {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-top:22px; }}
        .preview-field label {{ display:block; margin-bottom:6px; color:var(--muted); font-size:10px; }}
        .preview-field div {{ padding:9px 10px; border:1px solid var(--line); border-radius:4px; background:#121a2d; color:var(--cyan); font:400 10px 'IBM Plex Mono',monospace; }}
        .exchange-model {{ min-height:146px; margin:8px 0 8px; display:flex; align-items:center; justify-content:center; gap:24px; }}
        .participant {{ min-width:120px; padding:13px 18px; border:1px solid var(--line); border-radius:8px; text-align:center; }}
        .participant.channel {{ min-width:210px; }}
        .participant strong {{ display:block; font-size:19px; font-weight:400; }}
        .participant small {{ display:block; margin-top:4px; color:var(--cyan); font:400 8px 'IBM Plex Mono',monospace; }}
        .exchange-arrow {{ width:26px; }}
        .exchange-model > .icon {{ width:26px; height:20px; }}
        .decision-preview {{ padding:14px; display:flex; align-items:center; gap:12px; background:#121a2d; color:var(--muted); font-size:10px; }}
        .decision-preview img {{ width:18px; height:18px; }}
        .window-bottom {{ height:20px; background:#202020; }}
        .capabilities {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:44px; margin-top:44px; }}
        .capability-rule {{ width:40px; height:2px; margin-bottom:14px; background:var(--cyan); }}
        .capability-title {{ display:flex; align-items:center; gap:10px; margin-bottom:10px; font-size:14px; }}
        .capability-title img {{ width:19px; height:19px; }}
        .capability p {{ margin:0; color:var(--muted); font-size:12px; line-height:1.65; }}
        .protocol-hero {{ min-height:547px; padding:96px 48px 64px; position:relative; isolation:isolate; background-color:var(--panel); background-image:linear-gradient(90deg,rgba(3,5,13,.96) 0%,rgba(3,5,13,.56) 80%,rgba(3,5,13,.13) 100%),url('{wave_field}'); background-size:cover; background-position:center; }}
        .protocol-hero h2 {{ max-width:740px; margin:28px 0 22px; font-size:72px; font-weight:500; line-height:1.04; letter-spacing:-.04em; }}
        .protocol-hero p {{ max-width:530px; margin:0 0 22px; color:var(--muted); font-size:17px; line-height:1.65; }}
        .protocol-hero .caption {{ color:var(--muted); font:400 10px 'IBM Plex Mono',monospace; }}
        .protocol-details {{ padding:0 48px 88px; background:var(--panel); }}
        .rule {{ height:1px; background:var(--line); }}
        .protocol-grid {{ padding:32px 0; display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:32px; }}
        .protocol-card {{ min-height:175px; }}
        .stage-head {{ display:flex; align-items:center; justify-content:space-between; font-size:11px; }}
        .stage-head img {{ width:20px; height:20px; }}
        .protocol-card > img.icon {{ width:30px; height:30px; margin:18px 0 8px; }}
        .stage-icon {{ width:30px; height:30px; margin:18px 0 8px; }}
        .protocol-card h3 {{ margin:0 0 10px; color:var(--white); font-size:21px; font-weight:500; }}
        .protocol-card p {{ margin:0; color:var(--muted); font-size:14px; line-height:1.65; }}
        .interpretation {{ padding:28px; display:grid; grid-template-columns:1fr 1fr; gap:48px; border:1px solid var(--line); }}
        .interpretation h4 {{ margin:0 0 8px; color:var(--cyan); font:400 24px 'IBM Plex Mono',monospace; }}
        .interpretation strong {{ color:var(--white); font-size:16px; }}
        .interpretation p {{ margin:0; color:var(--muted); font-size:14px; line-height:1.65; }}
        .config-intro {{ max-width:950px; margin-bottom:60px; }}
        .config-intro .eyebrow {{ margin-bottom:22px; }}
        .config-intro h2 {{ margin:0 0 18px; font-size:58px; font-weight:500; line-height:1.04; letter-spacing:-.035em; }}
        .config-intro p {{ max-width:700px; margin:0; color:var(--muted); font-size:17px; line-height:1.65; }}
        .config-guide h3 {{ margin:0 0 16px; font-size:30px; font-weight:500; }}
        .parameter-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:24px; padding:24px 0; }}
        .parameter h4 {{ margin:0 0 6px; font-size:18px; font-weight:400; }}
        .parameter .mono {{ margin:0 0 9px; color:var(--cyan); font-size:12px; }}
        .parameter p {{ margin:0; color:var(--muted); font-size:14px; line-height:1.65; }}
        .limitation {{ color:var(--violet); font-size:13px; }}
        .comparison {{ margin-top:60px; }}
        .comparison .eyebrow {{ color:var(--violet); }}
        .comparison h3 {{ margin:10px 0 4px; color:var(--white); font-size:36px; font-weight:400; }}
        .comparison .sub-eyebrow {{ margin:0; color:var(--cyan); font:400 11px 'IBM Plex Mono',monospace; }}
        .boundary {{ margin:22px 0 30px; padding:12px 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); font-size:12px; }}
        .scenario {{ margin:30px 0; }}
        .scenario-title {{ display:flex; justify-content:space-between; gap:12px; align-items:center; margin-bottom:14px; }}
        .scenario-title h4 {{ margin:0; font-size:27px; font-weight:400; }}
        .scenario-title span {{ font:400 10px 'IBM Plex Mono',monospace; white-space:nowrap; }}
        .qber-track {{ height:64px; position:relative; overflow:visible; background:var(--panel-soft); }}
        .qber-fill {{ height:100%; }}
        .qber-fill.cyan {{ width:31%; background:var(--cyan); }}
        .qber-fill.violet {{ width:81%; background:var(--violet); }}
        .qber-boundary {{ position:absolute; left:54%; top:-8px; height:80px; width:1px; background:var(--white); }}
        .scenario > p {{ margin:10px 0 0; color:var(--muted); font-size:14px; }}
        .axis {{ display:flex; justify-content:space-between; margin:26px 0; color:var(--muted); font:400 10px 'IBM Plex Mono',monospace; }}
        .comparison-note {{ margin:0; color:var(--muted); font-size:14px; line-height:1.65; }}
        .methodology {{ padding-top:16px; }}
        .method-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:80px; margin-top:64px; }}
        .methodology .eyebrow {{ margin-bottom:24px; }}
        .method-copy {{ margin:22px 0; color:var(--muted); font-size:17px; line-height:1.65; }}
        .stack-row {{ padding:17px 0; display:grid; grid-template-columns:1fr 1fr; gap:20px; border-bottom:1px solid var(--line); }}
        .stack-row strong {{ font-size:20px; font-weight:400; }}
        .stack-row span {{ color:var(--muted); font-size:14px; }}
        .scope-card {{ padding:40px; background:var(--panel); }}
        .scope-card .eyebrow {{ color:var(--violet); }}
        .scope-item {{ margin-top:24px; }}
        .scope-item h3 {{ margin:0 0 10px; font-size:28px; font-weight:400; }}
        .scope-item p {{ margin:0; color:var(--muted); font-size:17px; line-height:1.65; }}
        .scope-card .rule {{ margin:24px 0; }}
        .scope-note {{ margin-top:24px!important; color:var(--violet)!important; font-size:14px!important; }}
        .invitation {{ padding:88px 48px; background:var(--cyan); color:#041116; }}
        .invitation .eyebrow {{ color:#041116; }}
        .invitation h2 {{ margin:30px 0 34px; color:#041116!important; font-size:clamp(42px,7vw,84px); font-weight:500; line-height:1.02; letter-spacing:-.045em; }}
        .invitation-row {{ display:grid; grid-template-columns:1fr 310px; gap:80px; align-items:center; }}
        .invitation-copy p {{ margin:0 0 14px; font-size:17px; line-height:1.6; }}
        .invitation-copy p:last-child {{ font-size:13px; }}
        .invitation-actions {{ display:flex; flex-direction:column; align-items:stretch; gap:16px; text-align:center; }}
        .invitation-actions a:last-child {{ font-size:13px; }}
        .footer {{ padding:48px; }}
        .footer-top, .footer-bottom {{ display:flex; justify-content:space-between; align-items:center; gap:24px; }}
        .footer-links {{ display:flex; gap:32px; font-size:14px; }}
        .footer .rule {{ margin:32px 0; }}
        .footer-bottom {{ color:var(--muted); font:400 10px/1.7 'IBM Plex Mono',monospace; }}
        @media(max-width:800px) {{
          .site-nav {{ min-height:76px; padding:14px 22px; }} .nav-links {{ display:none; }} .account-links {{ gap:12px; font-size:12px; }} .brand {{ min-width:0; }}
          .hero {{ min-height:690px; padding:76px 24px 90px; background-position:58% top; }} .hero h1 {{ font-size:clamp(48px,11vw,72px); }} .hero-caption {{ left:24px; right:24px; bottom:24px; }}
          .possibilities {{ padding:24px; grid-template-columns:1fr; gap:20px; }} .section {{ padding:76px 24px; }} .section-heading, .config-intro h2 {{ font-size:44px; }}
          .workspace-intro {{ grid-template-columns:1fr; gap:20px; }} .capabilities {{ grid-template-columns:1fr; gap:28px; }} .preview-body {{ padding:22px 18px; }} .preview-fields {{ grid-template-columns:1fr; }} .exchange-model {{ gap:8px; }} .participant {{ min-width:80px; padding:10px 8px; }} .participant.channel {{ min-width:110px; }} .participant strong {{ font-size:14px; }} .exchange-arrow {{ width:18px; }}
          .protocol-hero {{ min-height:500px; padding:76px 24px 42px; background-position:58% center; }} .protocol-hero h2 {{ font-size:clamp(44px,10vw,64px); }} .protocol-details {{ padding:0 24px 64px; }} .protocol-grid {{ grid-template-columns:1fr; gap:28px; }} .protocol-card {{ min-height:0; }} .interpretation {{ grid-template-columns:1fr; gap:24px; padding:22px; }}
          .parameter-grid {{ grid-template-columns:1fr; gap:22px; }} .scenario-title h4 {{ font-size:21px; }} .qber-track {{ height:48px; }}
          .method-grid {{ grid-template-columns:1fr; gap:32px; }} .scope-card {{ padding:28px; }} .invitation {{ padding:68px 24px; }} .invitation-row {{ grid-template-columns:1fr; gap:24px; }} .footer {{ padding:32px 24px; }} .footer-top {{ align-items:flex-start; flex-direction:column; }} .footer-links {{ flex-wrap:wrap; gap:18px; }} .footer-bottom {{ align-items:flex-start; flex-direction:column; gap:10px; }}
        }}
        @media(max-width:420px) {{ .account-links .button {{ min-height:42px; padding:0 12px; font-size:11px; }} .hero-actions .button {{ width:100%; }} .scenario-title {{ align-items:flex-start; flex-direction:column; }} .interpretation {{ padding:18px; }} }}
        </style>

        <main class="landing" id="top">
          <header class="site-nav">
            <a class="brand" href="#top" aria-label="SD-QKD Security Lab home">{icon('atom')}<span class="brand-name"><strong>SD-QKD</strong><small>SECURITY LAB</small></span></a>
            <nav class="nav-links" aria-label="Page sections"><a href="#workspace">Workspace</a><a href="#workflow">Workflow</a><a href="#methodology">Methodology</a></nav>
            <div class="account-links"><a href="?account=signin" target="_self">Sign in</a><a class="button button-primary" href="?account=signup" target="_self">Create researcher account{icon('arrow_up')}</a></div>
          </header>

          <section class="hero">
            <div class="eyebrow">SOFTWARE-ONLY, ACADEMIC RESEARCH</div>
            <h1>Superdense<br>Quantum Key<br>Distribution</h1>
            <div class="hero-copy">Explore simulated key exchange, introduce controlled eavesdropping, and examine how QBER shapes a quantum handshake decision.</div>
            <div class="hero-actions"><a class="button button-primary" href="?account=signup" target="_self">Create researcher account{icon('arrow_up')}</a><a class="button" href="#workflow">Explore the workflow{icon('arrow_down')}</a></div>
            <p class="hero-audience">For researchers, developers, and curious experimenters.</p>
            <div class="hero-caption"><span>ENTANGLEMENT / CONCEPTUAL VISUALIZATION</span><span>SCROLL TO INVESTIGATE ↓</span></div>
          </section>

          <section class="possibilities" aria-label="Research capabilities">
            <div><div class="eyebrow">01 / CONFIGURE</div><p>8-bit or 16-bit prototype sequences</p></div>
            <div><div class="eyebrow">02 / EXPERIMENT</div><p>Controlled Eve interference</p></div>
            <div><div class="eyebrow">03 / EVALUATE</div><p>QBER-based handshake decisions</p></div>
          </section>

          <section class="section" id="workspace">
            <div class="workspace-intro"><div><div class="eyebrow">01 / THE RESEARCH WORKSPACE</div><h2 class="section-heading">One workspace.<br>Every stage.</h2></div><p>Configure a simulation, review its security decision, and return to a clear record of each run—without physical quantum hardware.</p></div>
            <div class="preview-window" aria-label="Illustrative workspace preview, not a live run">
              <div class="window-bar"><span class="window-dot"></span><span class="window-dot"></span><span class="window-dot"></span><span class="window-title">Title</span></div>
              <div class="preview-body"><div class="eyebrow">WORKSPACE PREVIEW / NOT A LIVE RUN</div><h3>Live Simulation</h3>
                <div class="preview-tabs"><span>Simulation</span><span>Reports</span></div>
                <div class="preview-fields"><div class="preview-field"><label>Sequence size</label><div>8-bit&nbsp;&nbsp; / &nbsp;&nbsp;16-bit</div></div><div class="preview-field"><label>Simulation shots</label><div>Researcher-defined</div></div><div class="preview-field"><label>Eve interference</label><div>Disabled&nbsp;&nbsp; / &nbsp;&nbsp;Enabled</div></div></div>
                <div class="exchange-model"><div class="participant"><strong>Alice</strong><small>BELL PAIR + X/Z</small></div>{icon('arrow_right','')}<div class="participant channel"><strong>Simulated channel</strong><small>OPTIONAL EVE</small></div>{icon('arrow_right','')}<div class="participant"><strong>Bob</strong><small>DECODE + MEASURE</small></div></div>
                <div class="decision-preview">{icon('branch')}<span>QBER comparison → simulated accept / kill-switch → run history</span></div>
              </div><div class="window-bottom"></div>
            </div>
            <div class="capabilities">
              <div class="capability"><div class="capability-rule"></div><div class="capability-title">{icon('activity')}<span>Live Simulation</span></div><p>Choose a sequence size and shot count, toggle Eve, and follow QBER and the simulated handshake.</p></div>
              <div class="capability"><div class="capability-rule"></div><div class="capability-title">{icon('analytics')}<span>Reports &amp; Analytics</span></div><p>Review QBER trends, compare scenarios, and revisit logged experiments in run history.</p></div>
            </div>
          </section>

          <section id="workflow">
            <div class="protocol-hero"><div class="eyebrow">02 / FOLLOW THE PROTOCOL</div><h2>Make the invisible<br>exchange inspectable.</h2><p>Follow a software model from entanglement to a logged decision. Eve is an experimental variable—not a real network attacker.</p><div class="caption">A MODELED EXCHANGE, NOT A PHYSICAL CHANNEL</div></div>
            <div class="protocol-details"><div class="rule"></div><div class="protocol-grid">
              <article class="protocol-card"><div class="stage-head"><span class="eyebrow">01 / ALICE</span>{icon('arrow_right')}</div>{icon('binary')}<h3>Prepare &amp; encode</h3><p>Generate a Bell pair, then apply Pauli X/Z operations to encode the selected classical bit pairs.</p></article>
              <article class="protocol-card"><div class="stage-head"><span class="eyebrow" style="color:var(--violet)">02 / CHANNEL + EVE</span>{icon('arrow_right')}</div>{icon('scan_eye')}<h3>Introduce interference</h3><p>Enable or disable controlled Eve interference on the simulated quantum channel to compare scenarios.</p></article>
              <article class="protocol-card"><div class="stage-head"><span class="eyebrow">03 / BOB</span>{icon('arrow_right')}</div>{icon('scan_line')}<h3>Decode &amp; measure</h3><p>Decode the superdense states and measure the received sequence across the configured simulation shots.</p></article>
              <article class="protocol-card"><div class="stage-head"><span class="eyebrow">04 / EVALUATE</span>{icon('arrow_right')}</div>{icon('branch')}<h3>Compare &amp; log</h3><p>Compare QBER with the configured 11% threshold. Simulate handshake acceptance or a kill-switch, then log the run.</p></article>
            </div><div class="interpretation"><div><h4>QBER</h4><p>Quantum bit error rate: the fraction of compared bits that disagree.</p></div><div><strong>Workspace access ≠ quantum handshake</strong><p>Your username and password grant workspace access. The quantum handshake is a separate, simulated experiment.</p></div></div></div>
          </section>

          <section class="section" id="configuration">
            <div class="config-intro"><div class="eyebrow">03 / CHANGE A VARIABLE. EXAMINE THE EFFECT.</div><h2>From configuration<br>to comparison.</h2><p>Explore how your chosen settings affect the measured sequence and the simulated decision. Compare normal and interference scenarios with the same experimental lens.</p></div>
            <div class="config-guide"><h3>Set up your experiment</h3><div class="rule"></div><div class="parameter-grid">
              <div class="parameter"><h4>Sequence selection</h4><p class="mono">8-bit / 16-bit</p><p>Choose the prototype sequence length to explore encoding and comparison.</p></div>
              <div class="parameter"><h4>Simulation shots</h4><p class="mono">Researcher-defined</p><p>Set the number of repeated circuit measurements for the simulation.</p></div>
              <div class="parameter"><h4>Eve toggle</h4><p class="mono">Enabled / Disabled</p><p>Introduce controlled interference or explore a normal baseline scenario.</p></div>
            </div><div class="limitation">8-bit and 16-bit are prototype sequence sizes, not production security strengths.</div></div>
            <div class="comparison"><div class="eyebrow">REPORTS &amp; ANALYTICS / SCENARIO PREVIEW</div><h3>Read the decision boundary.</h3><p class="sub-eyebrow">QUALITATIVE ILLUSTRATION / NOT MEASURED RESULTS</p><div class="boundary mono">11% / CONFIGURED SIMULATION THRESHOLD</div>
              <div class="scenario"><div class="scenario-title"><h4>Normal / Eve disabled</h4><span style="color:var(--cyan)">BELOW BOUNDARY</span></div><div class="qber-track"><div class="qber-fill cyan"></div><div class="qber-boundary"></div></div><p>Illustrative outcome: simulated acceptance when QBER remains below the configured boundary.</p></div>
              <div class="scenario"><div class="scenario-title"><h4>Interference / Eve enabled</h4><span style="color:var(--violet)">ABOVE BOUNDARY</span></div><div class="qber-track"><div class="qber-fill violet"></div><div class="qber-boundary"></div></div><p>Illustrative outcome: simulated kill-switch when QBER crosses the configured boundary.</p></div>
              <div class="axis"><span>LOWER QBER</span><span>HIGHER QBER →</span></div><p class="comparison-note">Qualitative illustration—not measured results or a detection guarantee. Actual outcomes depend on the simulation settings. The 11% boundary is a configured simulation threshold, not a universal security guarantee.</p>
            </div>
          </section>

          <section class="section methodology" id="methodology"><div class="rule"></div><div class="method-grid">
            <div><div class="eyebrow">04 / METHOD &amp; RESEARCH SCOPE</div><h2 class="section-heading">Built to investigate,<br>not to certify.</h2><p class="method-copy">A Python-based academic simulator connects quantum circuit modeling with a readable experimental workflow. Inspect the protocol, vary the conditions, and interpret the record.</p><div class="stack-row"><strong>Python</strong><span>Core application</span></div><div class="stack-row"><strong>Qiskit / Qiskit Aer</strong><span>Quantum circuits / Simulation</span></div><div class="stack-row"><strong>Streamlit</strong><span>Research interface</span></div></div>
            <div class="scope-card"><div class="eyebrow">RESEARCH, WITH BOUNDARIES.</div><div class="scope-item"><h3>An experimental lens</h3><p>Models Bell pair generation, superdense encoding, controlled interference, measurement, and threshold-based simulated handshake decisions.</p></div><div class="rule"></div><div class="scope-item"><h3>Know the boundaries</h3><p>No physical quantum hardware or live quantum channel is used. Prototype results are for research and learning—not a security proof, production key distribution, or validation of real-world attack resistance.</p></div><p class="scope-note">This software-only academic prototype is not production security or proof of certificate-forgery prevention.</p></div>
          </div></section>

          <section class="invitation" id="account"><div class="eyebrow">YOUR NEXT EXPERIMENT STARTS HERE</div><h2>Bring your questions.<br>Explore the protocol.</h2><div class="invitation-row"><div class="invitation-copy"><p>Create a researcher account to enter the simulation workspace. Registration uses a username, password, and password confirmation.</p><p>Sign in and registration open in this page. Account authentication is distinct from the experimental handshake.</p></div><div class="invitation-actions"><a class="button button-dark" href="?account=signup" target="_self">Create researcher account{icon('arrow_up')}</a><a href="?account=signin" target="_self">Already have an account?&nbsp; Sign in →</a></div></div></section>

          <footer class="footer"><div class="footer-top"><a class="brand" href="#top">{icon('atom')}<span class="brand-name"><strong>SD-QKD</strong><small>SECURITY LAB</small></span></a><nav class="footer-links"><a href="#workspace">Workspace</a><a href="#workflow">Workflow</a><a href="#methodology">Methodology</a><a href="?account=signin" target="_self">Sign in</a></nav></div><div class="rule"></div><div class="footer-bottom"><span>SD-QKD SECURITY LAB / ACADEMIC PROTOTYPE</span><span>SOFTWARE-ONLY SIMULATION · NO PHYSICAL QUANTUM CHANNEL</span></div></footer>
        </main>
        """,
        unsafe_allow_html=True,
    )


render_landing_page()
