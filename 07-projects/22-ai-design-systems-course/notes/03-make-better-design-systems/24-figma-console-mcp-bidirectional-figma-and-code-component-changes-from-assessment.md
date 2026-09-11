---
title: Figma Console MCP — Bidirectional Figma and Code Fixes
section: "Chapter 3: Make Better Design Systems With AI"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/74979217-figma-console-mcp-bidirectional-figma-and-code-component-changes-from-assessment
duration: ~6m13s
status: noted
as-of: 2026-09-10
---

# Figma Console MCP - Bidirectional Figma and Code Component Changes From Assessment

From the audit: (1) success/error input treatment mismatch in code vs Figma; (2) missing inverted×disabled×success/error combos. One prompt: fix **both** legs; new Figma variants to the right of inverted.

Code fix is a stale mixin (`slpl-is-error` class rename never followed). Not invented CSS — following existing form-field architecture. Then Figma write: add missing variants. Old ping-pong (design→code→design) compressed; stuff still falls through, but the agent can pick both apples.
