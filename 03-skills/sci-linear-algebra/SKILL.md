---
name: sci-linear-algebra
description: >
  Context-free linear algebra for spatial computing — vectors, matrices, quaternions,
  bases and change-of-basis, affine vs. linear transforms, projection, and the camera/MVP
  pipeline. The backbone of every engine, shader, and rendering path. Triggers: vector,
  matrix, quaternion, dot/cross product, transform, rotation, basis, projection, MVP,
  homogeneous coordinates, normal matrix, SLERP.
aliases: [sci-linear-algebra]
triggers: [vector, matrix, quaternion, dot product, cross product, transform, rotation, basis, projection, mvp, homogeneous coordinates, slerp, normal matrix]
tier: foundation
hub: science-foundations
domain: science
surfaces: ["*"]
spec_version: "2.0"
---

# Foundations — Linear Algebra

The language of space. If a statement here weren't true for a game engine, a GPU shader, a robotics
arm, and a data projection alike, it would be in the wrong file.

## Vectors — the atom
A vector is a quantity with direction + magnitude in a named space. **Dot product** measures alignment
(`a·b = |a||b|cosθ` → projection, lighting's N·L, "are these facing the same way"). **Cross product**
yields a perpendicular (surface normals, torque, the handedness of a basis). Normalize before you reason
about direction; never compare un-normalized directions.

## Matrices — linear maps
A matrix *is* a linear transformation (it sends basis vectors to new ones — read its columns to see where
the axes go). Composition is multiplication, and **order matters** (`T·R ≠ R·T`). Distinguish **linear**
(rotate/scale/shear — origin-fixed) from **affine** (adds translation) — which is why 3D graphics uses
**homogeneous coordinates** (4×4, the `w` component) to make translation a matrix multiply.

## Rotations — and why quaternions
Euler angles gimbal-lock and interpolate badly. **Quaternions** represent 3D rotation without those
failures, compose cleanly, and **SLERP** between orientations smoothly — the right tool for camera and
character orientation. Convert to a matrix only at the boundary (GPU upload).

## The camera / MVP pipeline
Object → world → view → clip is just a chain of matrix multiplies: **Model · View · Projection**. The
**normal matrix** is the inverse-transpose of the model-view (normals transform differently than points
under non-uniform scale — a classic lighting bug). Knowing this chain is knowing how anything gets on screen.

## Bases + change-of-basis
Most "why is it rotated/offset wrong" bugs are a coordinate-space mismatch (world vs. local vs. view vs.
tangent space). Always name the space a vector lives in; transform deliberately between spaces.

## Related
- hub → [[science-foundations]]
- peer ↔ [[sci-numerical-methods]] · [[sci-physics-simulation]]
