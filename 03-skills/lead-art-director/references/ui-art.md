# UI Art Direction — Web Implementation (HTML/CSS/Canvas)

UI art is distinct from UX (interaction design). This covers the visual treatment, mood, and aesthetic of interface elements—how the NASA-industrial hard sci-fi style translates to screens, panels, and HUD in a web context.

## UI Art Direction for Hard Sci-Fi

### Diegetic vs Non-Diegetic

**Diegetic UI**: Exists in game world. Players see it on in-game screens, holograms, control panels.
- Rendered as WebGL/Three.js geometry (planes/quads with shader material) OR Canvas 2D overlay positioned in 3D space
- Examples: ship navigation display on bridge, factory status readout on wall monitor
- Aesthetic: Functional, utilitarian, grounded
- Typography: Monospaced, technical, readable at distance
- Color: Faction-specific (Colonial Authority = blue displays, Free Collective = amber/red)
- Wear: Can show damage, flickering, age

**Non-Diegetic UI**: Floating overlay, player-only. HUD, menus, inventory screen. Exists for player convenience, not in world.
- Rendered as HTML overlays on top of canvas OR Canvas 2D on top of renderer
- Aesthetic: Clean, minimalist, layered depth
- Typography: Sans-serif geometric (Eurostile) or monospaced technical
- Color: Consistent palette (accent color for highlights, neutral for background)
- Animation: Smooth, purposeful, responsive

**Best Practice for Legion**: Blend both.
- **First-person/in-world view**: Diegetic UI on in-game displays (Three.js shader materials or Canvas rendered to texture)
- **Menu navigation**: Non-diegetic HUD elements (HTML overlays or Canvas 2D on top)
- **Immersion**: Player never leaves the game world UI language. Menus reference faction displays, use same fonts.

---

## Implementation: Diegetic UI on In-Game Displays

### Approach 1: Canvas Texture Rendered to Three.js Material

Create dynamic in-world displays by rendering HTML/Canvas content to a texture:

```typescript
import * as THREE from 'three';

class DiegeticDisplay {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  texture: THREE.CanvasTexture;
  material: THREE.MeshStandardMaterial;
  mesh: THREE.Mesh;

  constructor(width: number = 512, height: number = 256) {
    // Create canvas
    this.canvas = document.createElement('canvas');
    this.canvas.width = width;
    this.canvas.height = height;
    this.ctx = this.canvas.getContext('2d')!;

    // Create texture from canvas
    this.texture = new THREE.CanvasTexture(this.canvas);
    this.texture.colorSpace = THREE.SRGBColorSpace;

    // Material that displays the texture with emissive glow
    this.material = new THREE.MeshStandardMaterial({
      map: this.texture,
      emissive: 0x001a3a,
      emissiveIntensity: 0.2,
      metalness: 0.1,
      roughness: 0.95
    });

    // Create quad mesh
    const geometry = new THREE.PlaneGeometry(2, 1);
    this.mesh = new THREE.Mesh(geometry, this.material);
  }

  // Render content to canvas
  drawContent(faction: 'colonial' | 'free' | 'synthetic') {
    const bgColor = faction === 'colonial' ? '#1a2a4a' : '#2a1a0a';
    const textColor = faction === 'colonial' ? '#00ff00' : '#ffaa00';

    // Clear and draw background
    this.ctx.fillStyle = bgColor;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw border
    this.ctx.strokeStyle = textColor;
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(4, 4, this.canvas.width - 8, this.canvas.height - 8);

    // Draw text (monospaced font)
    this.ctx.font = 'bold 16px "Courier New", monospace';
    this.ctx.fillStyle = textColor;
    this.ctx.fillText('FACTORY STATUS', 16, 30);
    this.ctx.font = '12px "Courier New", monospace';
    this.ctx.fillText('PROD: 245 units/min', 16, 60);
    this.ctx.fillText('POWER: 87%', 16, 85);

    // Signal that texture needs update
    this.texture.needsUpdate = true;
  }

  getMesh() {
    return this.mesh;
  }
}

// Usage
const factoryDisplay = new DiegeticDisplay(512, 256);
factoryDisplay.drawContent('colonial');
scene.add(factoryDisplay.getMesh());
```

---

### Approach 2: HTML Element Mapped to 3D Space

Use Three.js libraries like `three-mesh-ui` for interactive in-world UI:

```typescript
import * as THREE from 'three';
import MeshUIComponent from 'three-mesh-ui';

// Create in-world button
const button = new MeshUIComponent({
  width: 1.2,
  height: 0.4,
  padding: 0.05,
  justifyContent: 'center',
  alignItems: 'center',
  backgroundColor: new THREE.Color(0x1a2a4a),
  backgroundOpacity: 0.95,
  borderRadius: 0.01,
  borderWidth: 0.02,
  borderColor: 0x00ff00
});

// Add text
const text = new MeshUIComponent({
  content: 'ACTIVATE',
  fontFamily: './fonts/Courier Prime/Courier Prime_Regular.json',
  fontSize: 0.08,
  fontColor: new THREE.Color(0x00ff00),
  alignment: 'center'
});
button.add(text);

button.position.set(0, 1.5, -3);
scene.add(button);
```

---

## Implementation: Non-Diegetic HUD/Menus

### HTML Overlay Pattern

For menus, HUD elements, and player-only UI:

```html
<!-- HTML structure -->
<div id="hud-root" class="hud-container">
  <!-- Diegetic display: factory status -->
  <div class="hud-diegetic-display" style="position: fixed; top: 20px; right: 20px;">
    <div class="display-border">
      <div class="display-title">FACTORY STATUS</div>
      <div class="display-content">
        <div class="metric">PROD: <span class="value">245</span> units/min</div>
        <div class="metric">POWER: <span class="value">87%</span></div>
        <div class="metric">WORKERS: <span class="value">12/15</span></div>
      </div>
    </div>
  </div>

  <!-- Top-left: faction logo -->
  <div class="faction-logo colonial">
    <img src="logo-colonial-authority.svg" alt="Colonial Authority" />
  </div>

  <!-- Center: targeting reticle -->
  <div class="reticle"></div>
</div>
```

```css
/* Styling for hard sci-fi aesthetic */
.hud-container {
  font-family: 'Courier New', monospace;
  color: #00ff00;
  font-size: 12px;
  line-height: 1.5;
}

.display-border {
  border: 2px solid #00ff00;
  background-color: rgba(26, 42, 74, 0.8); /* dark blue, translucent */
  padding: 12px;
  box-shadow: inset 0 0 10px rgba(0, 255, 0, 0.2);
  min-width: 200px;
}

.display-title {
  font-weight: bold;
  text-align: center;
  border-bottom: 1px solid #00ff00;
  margin-bottom: 8px;
  padding-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.display-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
}

.metric .value {
  color: #00ff00;
  font-weight: bold;
  min-width: 60px;
  text-align: right;
}

/* Faction-specific styling */
.faction-logo.colonial {
  filter: hue-rotate(180deg); /* Blue tint */
}

.faction-logo.free {
  filter: sepia(0.3); /* Warm, aged look */
}

/* Reticle (targeting crosshair) */
.reticle {
  position: fixed;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  transform: translate(-50%, -50%);
  border: 2px solid #00ff00;
  pointer-events: none;
}

.reticle::before,
.reticle::after {
  content: '';
  position: absolute;
  background-color: #00ff00;
}

.reticle::before {
  width: 2px;
  height: 8px;
  left: 50%;
  top: -12px;
  transform: translateX(-50%);
}

.reticle::after {
  height: 2px;
  width: 8px;
  left: -12px;
  top: 50%;
  transform: translateY(-50%);
}
```

---

## Data Visualization Design

### Graphs & Charts in Canvas

```typescript
class DataGraph {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  data: number[] = [];

  constructor(containerId: string, width: number = 300, height: number = 150) {
    this.canvas = document.createElement('canvas');
    this.canvas.width = width;
    this.canvas.height = height;
    this.canvas.style.cssText = `
      border: 1px solid #00ff00;
      background-color: rgba(26, 42, 74, 0.8);
      display: block;
    `;
    document.getElementById(containerId)?.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d')!;
  }

  addDataPoint(value: number) {
    this.data.push(value);
    if (this.data.length > 60) this.data.shift(); // Keep last 60 points
    this.draw();
  }

  draw() {
    const w = this.canvas.width;
    const h = this.canvas.height;
    const padding = 20;

    // Clear
    this.ctx.fillStyle = 'rgba(26, 42, 74, 0.8)';
    this.ctx.fillRect(0, 0, w, h);

    // Grid
    this.ctx.strokeStyle = 'rgba(0, 255, 0, 0.1)';
    this.ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = padding + (i / 4) * (h - 2 * padding);
      this.ctx.beginPath();
      this.ctx.moveTo(padding, y);
      this.ctx.lineTo(w - padding, y);
      this.ctx.stroke();
    }

    // Plot line
    if (this.data.length > 1) {
      this.ctx.strokeStyle = '#00ff00';
      this.ctx.lineWidth = 2;
      this.ctx.beginPath();

      for (let i = 0; i < this.data.length; i++) {
        const x = padding + (i / (this.data.length - 1)) * (w - 2 * padding);
        const y = h - padding - (this.data[i] / 100) * (h - 2 * padding); // Assume 0-100 range

        if (i === 0) {
          this.ctx.moveTo(x, y);
        } else {
          this.ctx.lineTo(x, y);
        }
      }
      this.ctx.stroke();

      // Fill under line
      this.ctx.fillStyle = 'rgba(0, 255, 0, 0.1)';
      this.ctx.lineTo(w - padding, h - padding);
      this.ctx.lineTo(padding, h - padding);
      this.ctx.fill();
    }

    // Border
    this.ctx.strokeStyle = '#00ff00';
    this.ctx.lineWidth = 1;
    this.ctx.strokeRect(padding, padding, w - 2 * padding, h - 2 * padding);
  }
}

// Usage
const productionGraph = new DataGraph('graph-container', 300, 150);
setInterval(() => {
  productionGraph.addDataPoint(Math.random() * 100);
}, 1000);
```

---

## Icon Design for Web/Games

Use SVG for crisp, scalable icons:

```html
<svg class="icon icon-factory" width="32" height="32" viewBox="0 0 32 32">
  <g stroke="#00ff00" stroke-width="2" fill="none">
    <!-- Factory building shape -->
    <rect x="4" y="12" width="24" height="12" />
    <!-- Chimney -->
    <rect x="7" y="2" width="4" height="10" />
    <rect x="21" y="4" width="4" height="8" />
    <!-- Windows -->
    <circle cx="10" cy="16" r="2" />
    <circle cx="16" cy="16" r="2" />
    <circle cx="22" cy="16" r="2" />
  </g>
</svg>
```

```css
.icon {
  display: inline-block;
  color: #00ff00;
  vertical-align: middle;
}

.icon.active {
  color: #ffff00; /* Active state = yellow */
  filter: drop-shadow(0 0 4px #ffff00);
}

.icon.offline {
  color: #666666; /* Offline = gray */
}
```

---

## Button States & Interactions

### HTML Structure

```html
<button class="btn btn-primary colonial">
  <span class="btn-label">ACTIVATE</span>
</button>
```

### CSS Styling

```css
.btn {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  font-weight: bold;
  padding: 8px 16px;
  border: 2px solid;
  background-color: transparent;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 150ms ease-in-out;
  text-align: center;
  min-width: 100px;
}

/* Primary button (Colonial Authority style) */
.btn-primary.colonial {
  border-color: #0080ff;
  color: #0080ff;
  box-shadow: inset 0 0 8px rgba(0, 128, 255, 0.1);
}

.btn-primary.colonial:hover {
  background-color: rgba(0, 128, 255, 0.1);
  box-shadow: inset 0 0 12px rgba(0, 128, 255, 0.2), 0 0 8px rgba(0, 128, 255, 0.4);
}

.btn-primary.colonial:active {
  box-shadow: inset 0 0 16px rgba(0, 128, 255, 0.3);
  transform: scale(0.98);
}

.btn-primary.colonial:disabled {
  color: #555555;
  border-color: #555555;
  box-shadow: none;
  cursor: not-allowed;
}

/* Free Collective style */
.btn-primary.free {
  border-color: #ffaa00;
  color: #ffaa00;
  box-shadow: inset 0 0 8px rgba(255, 170, 0, 0.1);
}

.btn-primary.free:hover {
  background-color: rgba(255, 170, 0, 0.1);
  box-shadow: inset 0 0 12px rgba(255, 170, 0, 0.2), 0 0 8px rgba(255, 170, 0, 0.4);
}
```

---

## Animation & Motion Design

### Transitions

```css
/* Page/menu transitions */
.menu-page {
  animation: fadeIn 200ms ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Element stagger (list items appear in sequence) */
.menu-item {
  animation: slideIn 150ms ease-out forwards;
  opacity: 0;
}

.menu-item:nth-child(1) { animation-delay: 0ms; }
.menu-item:nth-child(2) { animation-delay: 50ms; }
.menu-item:nth-child(3) { animation-delay: 100ms; }

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### Loading Spinner

```html
<div class="spinner"></div>
```

```css
.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(0, 255, 0, 0.3);
  border-top: 2px solid #00ff00;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

---

## Gauges & Progress Bars

### HTML

```html
<div class="gauge">
  <div class="gauge-arc" style="--percentage: 75;"></div>
  <div class="gauge-label">75%</div>
</div>

<div class="progress-bar">
  <div class="progress-fill" style="width: 75%;"></div>
</div>
```

### CSS

```css
.gauge {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid #00ff00;
  display: flex;
  align-items: center;
  justify-content: center;
  background: conic-gradient(
    from 0deg,
    #00ff00 0deg,
    #00ff00 calc(var(--percentage) * 3.6deg),
    rgba(0, 255, 0, 0.1) calc(var(--percentage) * 3.6deg),
    rgba(0, 255, 0, 0.1) 360deg
  );
}

.gauge-label {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: bold;
  color: #00ff00;
}

.progress-bar {
  width: 200px;
  height: 16px;
  border: 1px solid #00ff00;
  background-color: rgba(0, 255, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #00ff00;
  transition: width 200ms ease-out;
  box-shadow: inset 0 0 4px rgba(0, 255, 0, 0.3);
}

.progress-fill.danger {
  background-color: #ff4444;
}

.progress-fill.warning {
  background-color: #ffaa00;
}
```

---

## Faction Color & Styling

**Colonial Authority**: Cool blue palette
- Primary color: #0080ff (operational blue)
- Text color: #00ff00 (operational green on dark backgrounds)
- Background: #1a2a4a (dark blue)
- Accent: white or bright blue

**Free Collective**: Warm amber palette
- Primary color: #ffaa00 (amber)
- Text color: #ffaa00 on dark backgrounds
- Background: #2a1a0a (dark brown)
- Accent: orange, worn aesthetic

**Synthetic Ascendant**: Sterile cyan
- Primary color: #00ffff (bright cyan)
- Text color: #00ffff on black backgrounds
- Background: #000000 (pure black)
- Accent: white, minimal design

---

## Typography & Readability

```css
/* Display font: geometric sans (simulating Eurostile) */
.title {
  font-family: 'Arial', sans-serif;
  font-size: 24px;
  font-weight: bold;
  letter-spacing: 2px;
  text-transform: uppercase;
  line-height: 1.2;
}

/* Body font: monospaced (simulating OCR-A) */
.body {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #00ff00;
}

/* Terminal/CRT aesthetic */
.terminal-text {
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #00ff00;
  background-color: #000000;
  padding: 8px;
  border: 1px solid #00ff00;
  text-shadow: 0 0 4px #00ff00;
  letter-spacing: 1px;
}

/* Readability: Ensure sufficient contrast */
/* WCAG AA: 4.5:1 ratio for normal text */
.ui-text {
  color: #00ff00;
  background-color: rgba(0, 0, 0, 0.8); /* Ensures contrast */
}
```

---

## Canvas 2D Overlay on Three.js

For HUD elements rendered directly as 2D over the 3D canvas:

```typescript
class CanvasHUD {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;

  constructor(renderer: THREE.WebGLRenderer) {
    // Create HUD canvas same size as renderer
    this.canvas = document.createElement('canvas');
    this.canvas.width = renderer.domElement.clientWidth;
    this.canvas.height = renderer.domElement.clientHeight;
    this.canvas.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      pointer-events: none;
    `;
    renderer.domElement.parentElement?.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d')!;
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawCrosshair(x: number, y: number, size: number = 20) {
    this.ctx.strokeStyle = '#00ff00';
    this.ctx.lineWidth = 2;

    // Horizontal
    this.ctx.beginPath();
    this.ctx.moveTo(x - size, y);
    this.ctx.lineTo(x + size, y);
    this.ctx.stroke();

    // Vertical
    this.ctx.beginPath();
    this.ctx.moveTo(x, y - size);
    this.ctx.lineTo(x, y + size);
    this.ctx.stroke();
  }

  drawText(text: string, x: number, y: number) {
    this.ctx.font = 'bold 12px "Courier New", monospace';
    this.ctx.fillStyle = '#00ff00';
    this.ctx.fillText(text, x, y);
  }

  drawFrame() {
    const margin = 20;
    this.ctx.strokeStyle = '#00ff00';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(margin, margin, this.canvas.width - 2 * margin, this.canvas.height - 2 * margin);
  }

  render(deltaTime: number) {
    this.clear();
    this.drawFrame();
    this.drawCrosshair(this.canvas.width / 2, this.canvas.height / 2);
    this.drawText(`FPS: ${Math.floor(1 / deltaTime)}`, 20, 40);
  }
}

// Usage in Three.js loop
const hud = new CanvasHUD(renderer);
function animate(currentTime: number) {
  const deltaTime = (currentTime - lastTime) / 1000;
  renderer.render(scene, camera);
  hud.render(deltaTime);
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
```

---

## Summary: Design System Thinking Applied to Game UI

**Tokens → CSS Variables**:
```css
:root {
  --color-primary-colonial: #0080ff;
  --color-primary-free: #ffaa00;
  --color-accent: #00ff00;
  --font-mono: 'Courier New', monospace;
  --font-sans: 'Arial', sans-serif;
  --spacing-small: 4px;
  --spacing-base: 8px;
  --spacing-large: 16px;
}

.btn {
  color: var(--color-accent);
  font-family: var(--font-mono);
  padding: var(--spacing-base) var(--spacing-large);
}
```

**Component Anatomy → HTML Structure**:
- Button states (default, hover, active, disabled) via CSS
- Faction variants via class names (`.colonial`, `.free`, `.synthetic`)
- Responsive behavior via media queries or CSS Grid

**Consistency**: Same button behavior and styling in menus and in-world HUD. Players experience unified UI language throughout.
