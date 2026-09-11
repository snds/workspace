import type { CanvasNode } from "@/types/canvas";

/**
 * Measure text dimensions using an offscreen canvas.
 * Returns { width, height } that tightly fit the given text
 * with the node's typography settings.
 */
export function measureText(node: Pick<CanvasNode, "text" | "fontSize" | "fontFamily" | "fontWeight" | "fontStyle" | "lineHeight" | "letterSpacing" | "textTransform">): { width: number; height: number } {
  const text = applyTextTransform(node.text ?? "", node.textTransform);
  const fontSize = node.fontSize ?? 16;
  const fontFamily = node.fontFamily ?? "Inter, sans-serif";
  const fontWeight = node.fontWeight ?? 400;
  const fontStyle = node.fontStyle ?? "normal";
  const lineHeight = node.lineHeight ?? 1.2;
  const letterSpacing = node.letterSpacing ?? 0;

  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d")!;
  ctx.font = `${fontStyle} ${fontWeight} ${fontSize}px ${fontFamily}`;

  const lines = text.split("\n");
  let maxWidth = 0;

  for (const line of lines) {
    let lineWidth = ctx.measureText(line).width;
    // Account for letter spacing (applied between all characters)
    if (letterSpacing !== 0 && line.length > 1) {
      lineWidth += letterSpacing * (line.length - 1);
    }
    maxWidth = Math.max(maxWidth, lineWidth);
  }

  const lineHeightPx = fontSize * lineHeight;
  const totalHeight = lines.length * lineHeightPx;

  // Add a small padding to prevent text from being clipped at edges
  return {
    width: Math.ceil(maxWidth) + 2,
    height: Math.ceil(totalHeight) + 2,
  };
}

function applyTextTransform(text: string, transform?: string): string {
  switch (transform) {
    case "uppercase": return text.toUpperCase();
    case "lowercase": return text.toLowerCase();
    case "capitalize": return text.replace(/\b\w/g, (c) => c.toUpperCase());
    default: return text;
  }
}
