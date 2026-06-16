"""
Generate a synthetic UI screenshot for smoke-testing the visual-qa-toolkit.
Produces a simple form-like layout with known misalignments, contrast issues,
and spacing to verify each check fires correctly.
"""
import cv2
import numpy as np
from pathlib import Path

W, H = 800, 600
bg = np.ones((H, W, 3), dtype=np.uint8) * 255

# Header bar
cv2.rectangle(bg, (0, 0), (W, 56), (33, 41, 57), -1)  # dark navy
cv2.putText(bg, "Settings", (32, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (240, 240, 240), 1, cv2.LINE_AA)

# Card container
cv2.rectangle(bg, (48, 96), (752, 528), (245, 247, 250), -1)
cv2.rectangle(bg, (48, 96), (752, 528), (220, 222, 226), 1)

# Label-input pairs, left-aligned at x=72 — with one intentionally off-by-3
labels = [
    ("Name",        72,  140),
    ("Email",       72,  200),
    ("Phone",       75,  260),   # intentionally 3px off
    ("Company",     72,  320),
    ("Website",     72,  380),
]
for text, x, y in labels:
    cv2.putText(bg, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (70, 80, 95), 1, cv2.LINE_AA)

# Input fields, starting at x=180, 16px gap vertical (on scale) except one orphan (19px)
inputs = [(180, 124, 548, 24), (180, 184, 548, 24), (180, 244, 548, 24),
          (180, 304, 548, 24), (180, 367, 548, 24)]  # last one: 63px gap from prev bottom→top = orphan
for (x, y, w, h) in inputs:
    cv2.rectangle(bg, (x, y), (x + w, y + h), (255, 255, 255), -1)
    cv2.rectangle(bg, (x, y), (x + w, y + h), (190, 195, 205), 1)

# Light gray "placeholder" text with poor contrast — should fail WCAG
cv2.putText(bg, "enter your name", (188, 142), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)
cv2.putText(bg, "name@example.com", (188, 202), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)
cv2.putText(bg, "(555) 000-0000", (188, 262), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)

# Primary button
cv2.rectangle(bg, (180, 440), (320, 472), (37, 99, 235), -1)
cv2.putText(bg, "Save Changes", (205, 461), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

# Cancel button
cv2.rectangle(bg, (336, 440), (440, 472), (245, 247, 250), -1)
cv2.rectangle(bg, (336, 440), (440, 472), (190, 195, 205), 1)
cv2.putText(bg, "Cancel", (368, 461), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (70, 80, 95), 1, cv2.LINE_AA)

out_path = Path(__file__).resolve().parent / "fixture_screenshot.png"
out_path.parent.mkdir(parents=True, exist_ok=True)
cv2.imwrite(str(out_path), bg)
print(f"Wrote {out_path}")
