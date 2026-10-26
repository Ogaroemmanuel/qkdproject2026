"""Shared interactive Three.js backdrop used by the public landing page."""

import streamlit as st


def render_quantum_background() -> None:
    """Render a lightweight pointer- and scroll-reactive particle field."""
    st.html(
        r"""
        <style>
          #sdqkd-quantum-field {
            position: fixed; inset: 0; z-index: 0; overflow: hidden;
            pointer-events: none; opacity: .56; mix-blend-mode: screen;
          }
          #sdqkd-quantum-field canvas { display: block; width: 100%; height: 100%; }
          [data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }
          @media (prefers-reduced-motion: reduce) {
            #sdqkd-quantum-field { opacity: .35; }
          }
        </style>
        <div id="sdqkd-quantum-field" aria-hidden="true"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
        (() => {
          const mount = document.getElementById("sdqkd-quantum-field");
          if (!mount || mount.dataset.ready) return;
          mount.dataset.ready = "true";

          const start = () => {
            if (!window.THREE || !mount.isConnected) return;
            const THREE = window.THREE;
            let width = window.innerWidth;
            let height = window.innerHeight;
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(52, width / height, .1, 100);
            camera.position.z = 22;
            const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
            renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
            renderer.setSize(width, height);
            renderer.setClearColor(0x03050d, 0);
            mount.appendChild(renderer.domElement);

            const count = width < 700 ? 420 : 900;
            const positions = new Float32Array(count * 3);
            const colors = new Float32Array(count * 3);
            const cyan = new THREE.Color(0x74f5ff);
            const violet = new THREE.Color(0xae8cff);
            for (let i = 0; i < count; i += 1) {
              positions[i * 3] = (Math.random() - .5) * 43;
              positions[i * 3 + 1] = (Math.random() - .5) * 27;
              positions[i * 3 + 2] = (Math.random() - .5) * 24;
              const color = Math.random() > .76 ? violet : cyan;
              colors[i * 3] = color.r;
              colors[i * 3 + 1] = color.g;
              colors[i * 3 + 2] = color.b;
            }
            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
            const particles = new THREE.Points(
              geometry,
              new THREE.PointsMaterial({ size: .075, vertexColors: true, transparent: true, opacity: .76, depthWrite: false })
            );
            scene.add(particles);

            const rings = new THREE.Group();
            for (let i = 0; i < 3; i += 1) {
              const ring = new THREE.Mesh(
                new THREE.TorusGeometry(4 + i * .9, .012, 6, 150),
                new THREE.MeshBasicMaterial({ color: i === 1 ? 0xae8cff : 0x74f5ff, transparent: true, opacity: .23 })
              );
              ring.rotation.set(.72 + i * .16, i * .7, .2 + i * .38);
              rings.add(ring);
            }
            rings.position.set(9, 1.8, -4);
            scene.add(rings);

            let pointerX = 0;
            let pointerY = 0;
            let scrollProgress = 0;
            const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
            const onPointer = (event) => {
              pointerX = (event.clientX / Math.max(width, 1) - .5) * 2;
              pointerY = (event.clientY / Math.max(height, 1) - .5) * 2;
              document.querySelectorAll(".auth-brand").forEach((panel) => {
                const bounds = panel.getBoundingClientRect();
                if (bounds.width && bounds.height) {
                  const dx = (event.clientX - bounds.left) / bounds.width - .5;
                  const dy = (event.clientY - bounds.top) / bounds.height - .5;
                  panel.style.setProperty("--auth-x", `${dx * 18}px`);
                  panel.style.setProperty("--auth-y", `${dy * 18}px`);
                }
              });
            };
            const onScroll = () => {
              const range = Math.max(document.documentElement.scrollHeight - height, 1);
              scrollProgress = window.scrollY / range;
            };
            const onResize = () => {
              width = window.innerWidth;
              height = window.innerHeight;
              camera.aspect = width / height;
              camera.updateProjectionMatrix();
              renderer.setSize(width, height);
            };
            const teardown = () => {
              renderer.setAnimationLoop(null);
              window.removeEventListener("pointermove", onPointer);
              window.removeEventListener("scroll", onScroll);
              window.removeEventListener("resize", onResize);
              renderer.dispose();
              observer.disconnect();
            };
            window.addEventListener("pointermove", onPointer, { passive: true });
            window.addEventListener("scroll", onScroll, { passive: true });
            window.addEventListener("resize", onResize, { passive: true });
            const observer = new MutationObserver(() => {
              if (!mount.isConnected) teardown();
            });
            observer.observe(document.body, { childList: true, subtree: true });
            renderer.setAnimationLoop((time) => {
              const t = time * .00012;
              particles.rotation.y = reducedMotion ? 0 : t + pointerX * .035;
              particles.rotation.x = reducedMotion ? 0 : pointerY * .025 + scrollProgress * .12;
              rings.rotation.y = reducedMotion ? 0 : -t * .7 + pointerX * .06;
              rings.rotation.x = reducedMotion ? .8 : .8 + pointerY * .04 + scrollProgress * .18;
              camera.position.x += (pointerX * .42 - camera.position.x) * .025;
              camera.position.y += (-pointerY * .28 - camera.position.y) * .025;
              camera.lookAt(0, 0, 0);
              renderer.render(scene, camera);
            });
          };

          if (window.THREE) start();
          else {
            const threeScript = document.querySelector('script[src*="three.min.js"]');
            if (threeScript) threeScript.addEventListener("load", start, { once: true });
          }
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )
