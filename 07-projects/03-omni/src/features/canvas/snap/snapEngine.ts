/**
 * Snap engine — pure functions for calculating snap alignments.
 *
 * Inspired by Penpot's snap system: queries X and Y axes independently,
 * finds the minimum distance snap for each axis, combines into a delta vector.
 */

export interface Bounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface SnapResult {
  /** The value to snap to (world coordinate) */
  snapTo: number;
  /** Delta to apply to the moving shape's edge/center */
  delta: number;
  /** Guide line start/end (world coords, for visual rendering) */
  guideStart: number;
  guideEnd: number;
  /** Which axis this snap applies to */
  axis: "x" | "y";
  /** Type of snap alignment */
  type: "edge" | "center";
  /** The position on the perpendicular axis where the guide line lives */
  guidePosition: number;
}

export interface SnapOutput {
  dx: number;
  dy: number;
  guides: SnapResult[];
}

// ─── Snap point extraction ────────────────────────────────────────────────────

interface SnapPoints {
  /** Left, center, right edges */
  xPoints: number[];
  /** Top, center, bottom edges */
  yPoints: number[];
}

function getSnapPoints(bounds: Bounds): SnapPoints {
  return {
    xPoints: [bounds.x, bounds.x + bounds.width / 2, bounds.x + bounds.width],
    yPoints: [bounds.y, bounds.y + bounds.height / 2, bounds.y + bounds.height],
  };
}

// ─── Core snap calculation ────────────────────────────────────────────────────

/**
 * Find the closest snap alignment between a moving set of bounds and
 * a list of candidate nodes.
 *
 * @param movingBounds - Bounds of the shape(s) being moved/resized
 * @param candidates - Other nodes to snap against (excludes moving nodes)
 * @param tolerance - Maximum snap distance in world pixels (typically 10/zoom)
 */
export function findSnaps(
  movingBounds: Bounds,
  candidates: Bounds[],
  tolerance: number,
): SnapOutput {
  const movingPts = getSnapPoints(movingBounds);
  let bestX: SnapResult | null = null;
  let bestY: SnapResult | null = null;

  for (const candidate of candidates) {
    const candPts = getSnapPoints(candidate);

    // ── X axis snaps (vertical guide lines) ─────────────────────────────────
    for (const mx of movingPts.xPoints) {
      for (const cx of candPts.xPoints) {
        const dist = Math.abs(mx - cx);
        if (dist < tolerance && (!bestX || dist < Math.abs(bestX.delta))) {
          const isCenter =
            mx === movingBounds.x + movingBounds.width / 2 &&
            cx === candidate.x + candidate.width / 2;
          // Guide line spans both shapes vertically
          const minY = Math.min(movingBounds.y, candidate.y);
          const maxY = Math.max(
            movingBounds.y + movingBounds.height,
            candidate.y + candidate.height,
          );
          bestX = {
            snapTo: cx,
            delta: cx - mx,
            guideStart: minY,
            guideEnd: maxY,
            axis: "x",
            type: isCenter ? "center" : "edge",
            guidePosition: cx,
          };
        }
      }
    }

    // ── Y axis snaps (horizontal guide lines) ────────────────────────────────
    for (const my of movingPts.yPoints) {
      for (const cy of candPts.yPoints) {
        const dist = Math.abs(my - cy);
        if (dist < tolerance && (!bestY || dist < Math.abs(bestY.delta))) {
          const isCenter =
            my === movingBounds.y + movingBounds.height / 2 &&
            cy === candidate.y + candidate.height / 2;
          const minX = Math.min(movingBounds.x, candidate.x);
          const maxX = Math.max(
            movingBounds.x + movingBounds.width,
            candidate.x + candidate.width,
          );
          bestY = {
            snapTo: cy,
            delta: cy - my,
            guideStart: minX,
            guideEnd: maxX,
            axis: "y",
            type: isCenter ? "center" : "edge",
            guidePosition: cy,
          };
        }
      }
    }
  }

  const guides: SnapResult[] = [];
  if (bestX) guides.push(bestX);
  if (bestY) guides.push(bestY);

  return {
    dx: bestX?.delta ?? 0,
    dy: bestY?.delta ?? 0,
    guides,
  };
}

/**
 * Find snap alignment for specific edges during resize.
 * Only checks the edge(s) being dragged (determined by handleDx/handleDy).
 *
 * @param bounds      Current proposed bounds of the resized shape(s)
 * @param handleDx    -1 = left edge, 1 = right edge, 0 = no horizontal resize
 * @param handleDy    -1 = top edge, 1 = bottom edge, 0 = no vertical resize
 * @param candidates  Other nodes to snap against
 * @param tolerance   Maximum snap distance in world pixels
 */
export function findResizeSnaps(
  bounds: Bounds,
  handleDx: number,
  handleDy: number,
  candidates: Bounds[],
  tolerance: number,
): SnapOutput {
  let bestX: SnapResult | null = null;
  let bestY: SnapResult | null = null;

  // Determine which edge to check on each axis
  const myXEdge = handleDx === 1 ? bounds.x + bounds.width : handleDx === -1 ? bounds.x : null;
  const myYEdge = handleDy === 1 ? bounds.y + bounds.height : handleDy === -1 ? bounds.y : null;

  for (const cand of candidates) {
    const cp = getSnapPoints(cand);

    if (myXEdge !== null) {
      for (const cx of cp.xPoints) {
        const dist = Math.abs(myXEdge - cx);
        if (dist < tolerance && (!bestX || dist < Math.abs(bestX.delta))) {
          const minY = Math.min(bounds.y, cand.y);
          const maxY = Math.max(bounds.y + bounds.height, cand.y + cand.height);
          bestX = {
            snapTo: cx, delta: cx - myXEdge,
            guideStart: minY, guideEnd: maxY,
            axis: "x", type: "edge", guidePosition: cx,
          };
        }
      }
    }

    if (myYEdge !== null) {
      for (const cy of cp.yPoints) {
        const dist = Math.abs(myYEdge - cy);
        if (dist < tolerance && (!bestY || dist < Math.abs(bestY.delta))) {
          const minX = Math.min(bounds.x, cand.x);
          const maxX = Math.max(bounds.x + bounds.width, cand.x + cand.width);
          bestY = {
            snapTo: cy, delta: cy - myYEdge,
            guideStart: minX, guideEnd: maxX,
            axis: "y", type: "edge", guidePosition: cy,
          };
        }
      }
    }
  }

  const guides: SnapResult[] = [];
  if (bestX) guides.push(bestX);
  if (bestY) guides.push(bestY);

  return { dx: bestX?.delta ?? 0, dy: bestY?.delta ?? 0, guides };
}
