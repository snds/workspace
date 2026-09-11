---
title: Why MCPs matter
section: "Chapter 1: AI & Design Systems Core Concepts"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/74427618-why-mcps-matter
duration: ~1m39s
status: noted
as-of: 2026-09-10
---

# Why MCPs matter

Before MCP: custom glue (Make, n8n, hand-rolled API tethers). MCP: plug the client into the platform with no glue code / third-party dependency.

The model sees **live work**, not a paste or a static dump. Gmail example: ask twice, get new mail the second time without re-pasting. Claim: live connection **lowers hallucination risk** because answers are fetched, not guessed.

## For Sean

True when the MCP is a real read of a system of record. False if the MCP returns smoothed/partial context (the “testimony not contract” trap). Keep that distinction for Figma MCP vs Figma Console MCP later.
