"""
Generate synthetic fixtures for the three checks not covered by the main
fixture_screenshot.png:
  - visual_diff: a "reference" vs. "implementation" pair with planted drift
  - icon_consistency: a folder of icons with one outlier
  - state_comparison: a folder of component states, with hover ≈ default planted
"""
import cv2
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROOT.mkdir(exist_ok=True)


def make_visual_diff_pair():
    """Two 600×400 images — implementation has a small drift vs. reference."""
    ref = np.ones((400, 600, 3), dtype=np.uint8) * 250
    # Header
    cv2.rectangle(ref, (0, 0), (600, 48), (33, 41, 57), -1)
    cv2.putText(ref, "Dashboard", (24, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 1, cv2.LINE_AA)
    # Card
    cv2.rectangle(ref, (24, 72), (576, 360), (255, 255, 255), -1)
    cv2.rectangle(ref, (24, 72), (576, 360), (220, 222, 226), 1)
    cv2.putText(ref, "Card Title", (40, 104), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 40), 1, cv2.LINE_AA)
    # Button
    cv2.rectangle(ref, (40, 300), (140, 332), (37, 99, 235), -1)
    cv2.putText(ref, "Save", (68, 321), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    impl = ref.copy()
    # Planted drift: button shifted 6px right, different primary color
    cv2.rectangle(impl, (40, 300), (140, 332), (255, 255, 255), -1)  # erase
    cv2.rectangle(impl, (46, 300), (146, 332), (45, 110, 220), -1)   # new position + shade
    cv2.putText(impl, "Save", (74, 321), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    # Planted drift: title shifted 2px down
    cv2.rectangle(impl, (40, 88), (200, 112), (255, 255, 255), -1)
    cv2.putText(impl, "Card Title", (40, 106), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 40), 1, cv2.LINE_AA)

    cv2.imwrite(str(ROOT / "diff_reference.png"), ref)
    cv2.imwrite(str(ROOT / "diff_implementation.png"), impl)
    print(f"Wrote visual_diff pair")


def make_icon_set():
    """Eight simulated icons — seven consistent, one outlier (too heavy)."""
    icons_dir = ROOT / "icons"
    icons_dir.mkdir(exist_ok=True)

    for existing in icons_dir.glob("*.png"):
        existing.unlink()

    # Seven normal icons — simple 24x24 strokes at stroke-width 2
    shapes = {
        "plus":     lambda c: (cv2.line(c, (12, 4), (12, 20), 0, 2), cv2.line(c, (4, 12), (20, 12), 0, 2)),
        "minus":    lambda c: cv2.line(c, (4, 12), (20, 12), 0, 2),
        "cross":    lambda c: (cv2.line(c, (5, 5), (19, 19), 0, 2), cv2.line(c, (19, 5), (5, 19), 0, 2)),
        "check":    lambda c: (cv2.line(c, (5, 13), (10, 18), 0, 2), cv2.line(c, (10, 18), (20, 6), 0, 2)),
        "arrow_l":  lambda c: (cv2.line(c, (4, 12), (14, 4), 0, 2), cv2.line(c, (4, 12), (14, 20), 0, 2), cv2.line(c, (4, 12), (20, 12), 0, 2)),
        "arrow_r":  lambda c: (cv2.line(c, (20, 12), (10, 4), 0, 2), cv2.line(c, (20, 12), (10, 20), 0, 2), cv2.line(c, (4, 12), (20, 12), 0, 2)),
        "circle":   lambda c: cv2.circle(c, (12, 12), 8, 0, 2),
    }
    for name, drawer in shapes.items():
        canvas = np.full((24, 24, 4), 255, dtype=np.uint8)
        canvas[:, :, :3] = 255
        canvas[:, :, 3] = 0  # fully transparent bg
        # Draw on RGB, then set alpha where drawn
        rgb = np.full((24, 24, 3), 255, dtype=np.uint8)
        drawer(rgb)
        # Alpha: non-white → opaque
        mask = (rgb != 255).any(axis=2).astype(np.uint8) * 255
        canvas[:, :, 0] = rgb[:, :, 0]
        canvas[:, :, 1] = rgb[:, :, 1]
        canvas[:, :, 2] = rgb[:, :, 2]
        canvas[:, :, 3] = mask
        cv2.imwrite(str(icons_dir / f"{name}.png"), canvas)

    # Outlier: thick filled circle — much heavier than the rest
    outlier = np.full((24, 24, 4), 255, dtype=np.uint8)
    outlier_rgb = np.full((24, 24, 3), 255, dtype=np.uint8)
    cv2.circle(outlier_rgb, (12, 12), 10, 0, -1)  # filled, very heavy
    mask = (outlier_rgb != 255).any(axis=2).astype(np.uint8) * 255
    outlier[:, :, :3] = outlier_rgb
    outlier[:, :, 3] = mask
    cv2.imwrite(str(icons_dir / "OUTLIER_filled_disc.png"), outlier)

    print(f"Wrote 8 icons to {icons_dir}")


def make_state_set():
    """Five state screenshots — hover planted to be nearly identical to default."""
    states_dir = ROOT / "states"
    states_dir.mkdir(exist_ok=True)
    for existing in states_dir.glob("*.png"):
        existing.unlink()

    def render_button(bg_color, border_color, text_color, y_offset=0, label="Button"):
        img = np.full((80, 240, 3), 248, dtype=np.uint8)
        cv2.rectangle(img, (20, 24 + y_offset), (220, 56 + y_offset), bg_color, -1)
        cv2.rectangle(img, (20, 24 + y_offset), (220, 56 + y_offset), border_color, 1)
        cv2.putText(img, label, (78, 46 + y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 1, cv2.LINE_AA)
        return img

    # Planted: hover ≈ default (only 1 pixel difference in bg color) — should flag
    default_img = render_button((37, 99, 235), (30, 80, 200), (255, 255, 255))
    hover_img = render_button((38, 100, 236), (30, 80, 200), (255, 255, 255))  # ~identical
    focus_img = render_button((37, 99, 235), (30, 80, 200), (255, 255, 255))
    # Add focus ring
    cv2.rectangle(focus_img, (16, 20), (224, 60), (139, 92, 246), 2)
    active_img = render_button((25, 70, 180), (15, 50, 140), (255, 255, 255))  # darker
    disabled_img = render_button((200, 210, 225), (180, 190, 205), (150, 150, 160))  # desaturated

    cv2.imwrite(str(states_dir / "default.png"), default_img)
    cv2.imwrite(str(states_dir / "hover.png"), hover_img)
    cv2.imwrite(str(states_dir / "focus.png"), focus_img)
    cv2.imwrite(str(states_dir / "active.png"), active_img)
    cv2.imwrite(str(states_dir / "disabled.png"), disabled_img)
    print(f"Wrote 5 state images to {states_dir}")


if __name__ == "__main__":
    make_visual_diff_pair()
    make_icon_set()
    make_state_set()
