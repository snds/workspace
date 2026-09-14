# Shapr3D MCP setup

SessionID: 2026-09-14-shapr3d-mcp-setup
Date: 2026-09-14
Agent · Surface · Machine: GPT-6 · Codex desktop · Work MacBook Pro
Context profile: personal-solo, explicitly declared by Sean.
Project home: temporary name `Projects/shapr3d-personal`; final project concept/name pending reference. No numbered vault project allocated yet.

## Live handoff

- Installed Alfredoalv13/shapr3d-mcp revision `88fcefe` in the sibling Projects checkout with frozen uv dependencies.
- Registered `shapr3d` globally using the Codex CLI; read-back confirms enabled. Project config alone was not loaded by this parent task. Native tool refresh requires restart; real MCP client connection tested successfully.
- All 30 upstream tests pass. Generated test plate STEP + STL; independent mesh topology, 60 × 40 × 8 mm bounds, and analytic volume checks pass (0.00205% volume error).
- Sean installed and launched Shapr3D during the session. The server app bridge opened the STL; Computer Use observed the imported plate with four holes and captured the app window.
- Evidence and portable setup notes: `Projects/shapr3d-personal/README.md`, `validation.json`, `models/shapr3d_stl_import.png`, and reproducible smoke script.
- Upstream executes unrestricted Python. Screenshot tool falls back to entire display; prefer app-targeted Computer Use. STEP is editable-solid interchange, without feature history; STL is a mesh.
- Next: receive visual reference and dimensions; establish final project identity, create versioned models, and inspect in Shapr3D. STEP app import and app-side measurements remain unverified.
- No employer repository modified. No conceptual design work started.
