# Build, Test, and Deploy: Getting Legion to Players (Web)

From source code to shipped game. Build pipeline, testing, profiling, and deployment strategies for Legion on the web.

## Vite Build Pipeline

### Project Setup

```bash
# Create a new Vite + Three.js project
npm create vite@latest legion-game -- --template vanilla

cd legion-game
npm install three cannon-es typescript
```

### vite.config.ts

```typescript
import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
  server: {
    port: 3000,
    strictPort: false
  },

  build: {
    target: "esnext",
    minify: "terser",
    sourcemap: process.env.NODE_ENV === "development",
    rollupOptions: {
      output: {
        // Code splitting strategy
        manualChunks: {
          three: ["three"],
          physics: ["cannon-es"],
          gameplay: ["./src/core", "./src/systems"]
        }
      }
    }
  },

  optimizeDeps: {
    include: ["three", "cannon-es"]
  }
});
```

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "declaration": true,
    "outDir": "./dist",
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "types": ["vite/client"]
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### Build Commands

```bash
# Development server with hot reload
npm run dev

# Build for production (optimized, minified)
npm run build

# Preview the production build locally
npm run preview
```

## Automated Testing

### Unit Tests with Vitest

```typescript
// tests/production.test.ts
import { describe, it, expect } from "vitest";
import { ProductionComponent } from "../src/core/components/ProductionComponent";
import { Entity } from "../src/core/Entity";

describe("ProductionComponent", () => {
  it("should accumulate production over time", () => {
    const entity = new Entity("factory_test");
    const production = new ProductionComponent({
      rate: 10,
      inputs: {},
      output: "iron"
    });
    entity.addComponent(production);

    production.startProduction();
    production.update(1.0); // 1 second

    expect(production["accumulatedOutput"]).toBeCloseTo(10, 1);
  });

  it("should emit items when accumulated", () => {
    const entity = new Entity("factory_test");
    const production = new ProductionComponent({
      rate: 10,
      inputs: {},
      output: "iron"
    });
    entity.addComponent(production);

    let emitted = false;
    production.onItemProduced.on(() => {
      emitted = true;
    });

    production.startProduction();
    production.update(0.2); // Produce 2 items

    expect(emitted).toBe(true);
  });

  it("should stop production when storage is full", () => {
    const entity = new Entity("factory_test");
    const production = new ProductionComponent({
      rate: 10,
      inputs: {},
      output: "iron"
    });
    const storage = new StorageComponent({ iron: 100 });

    entity.addComponent(production);
    entity.addComponent(storage);

    // Fill storage
    storage.addResource("iron", 100);

    production.startProduction();
    production.update(1.0);

    expect(production["accumulatedOutput"]).toBe(0); // Should stop
  });
});
```

Run tests:
```bash
npm install -D vitest @vitest/ui
npm run test
```

### Integration Tests with Playwright

```typescript
// tests/integration.test.ts
import { test, expect } from "@playwright/test";

test.describe("Legion Game", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3000");
    await page.waitForLoadState("networkidle");
  });

  test("should load the game", async ({ page }) => {
    const canvas = await page.$("canvas");
    expect(canvas).toBeTruthy();
  });

  test("should save game to IndexedDB", async ({ page }) => {
    // Simulate building construction
    await page.click("#build-button");
    await page.fill("#building-type", "factory_basic");
    await page.click("#confirm-build");

    // Save game
    await page.click("#save-button");
    await page.fill("#save-name", "test_save");
    await page.click("#confirm-save");

    // Check IndexedDB
    const savedGames = await page.evaluate(() => {
      return new Promise((resolve) => {
        const request = indexedDB.open("legion-saves");
        request.onsuccess = () => {
          const db = request.result;
          const tx = db.transaction(["games"], "readonly");
          const store = tx.objectStore("games");
          const getRequest = store.getAll();
          getRequest.onsuccess = () => {
            resolve(getRequest.result);
          };
        };
      });
    });

    expect((savedGames as any).length).toBeGreaterThan(0);
  });

  test("should handle production correctly", async ({ page }) => {
    // Build a factory
    await page.click("#build-button");
    await page.fill("#building-type", "factory_basic");
    await page.click("#confirm-build");

    // Wait for production to accumulate
    await page.waitForTimeout(2000);

    // Check inventory increased
    const inventory = await page.textContent("#inventory-iron");
    const amount = parseInt(inventory?.split(": ")[1] ?? "0");

    expect(amount).toBeGreaterThan(0);
  });
});
```

Run integration tests:
```bash
npm install -D @playwright/test
npx playwright install
npm run test:integration
```

### CI/CD with GitHub Actions

```yaml
# .github/workflows/build-test.yml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run unit tests
        run: npm run test

      - name: Build project
        run: npm run build

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        if: matrix.node-version == '20.x'

  integration-tests:
    runs-on: ubuntu-latest
    needs: build

    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 20.x

      - name: Install dependencies
        run: npm ci

      - name: Build project
        run: npm run build

      - name: Install Playwright browsers
        run: npx playwright install

      - name: Run integration tests
        run: npm run test:integration

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

## Performance Profiling

### Chrome DevTools Profiling

1. Open DevTools → Performance tab
2. Click Record, play for 10 seconds
3. Click Stop
4. Analyze the flame graph

Look for:
- Long paint operations (GPU-bound)
- Long JavaScript execution (CPU-bound)
- Memory growth (memory leaks)

### Real-Time Profiling with Stats.js

```typescript
import Stats from "three/examples/jsm/libs/stats.module.js";

const stats = new Stats();
document.body.appendChild(stats.dom);

function animate() {
  stats.begin();

  // Game update logic
  scene.traverse((obj) => {
    if (obj instanceof Entity) obj.update();
  });

  renderer.render(scene, camera);
  stats.end();

  requestAnimationFrame(animate);
}

animate();
```

### Renderer Info Monitoring

```typescript
class PerformanceMonitor {
  private renderer: THREE.WebGLRenderer;
  private stats: any;

  constructor(renderer: THREE.WebGLRenderer) {
    this.renderer = renderer;
  }

  logPerformanceMetrics(): void {
    const info = this.renderer.info;

    console.log("=== Performance Metrics ===");
    console.log(`Draw calls: ${info.render.calls}`);
    console.log(`Triangles: ${info.render.triangles}`);
    console.log(`Textures: ${info.memory.textures}`);
    console.log(`Geometries: ${info.memory.geometries}`);
    console.log(`Programs: ${info.programs?.length ?? "N/A"}`);
  }

  optimizeIfNeeded(): void {
    const info = this.renderer.info;

    // If too many draw calls, suggest batching
    if (info.render.calls > 500) {
      console.warn("High draw call count. Consider using InstancedMesh or batching.");
    }

    // If high triangle count, suggest LOD
    if (info.render.triangles > 5000000) {
      console.warn("High triangle count. Consider using LOD.");
    }

    // If memory usage high, suggest pooling or disposal
    const totalMemory =
      (info.memory.textures ?? 0) + (info.memory.geometries ?? 0);
    if (totalMemory > 500) {
      console.warn("High memory usage. Check for undisposed geometries/textures.");
    }
  }
}
```

## Browser Compatibility & Fallbacks

### WebGPU/WebGL Detection

```typescript
class GraphicsCapability {
  static async detectCapabilities(): Promise<{
    hasWebGPU: boolean;
    webglVersion: "webgl" | "webgl2";
    maxTextureSize: number;
  }> {
    const canvas = document.createElement("canvas");

    // Check WebGPU
    const hasWebGPU = !!(navigator as any).gpu;

    // Check WebGL
    let webglVersion: "webgl" | "webgl2" = "webgl";
    if (canvas.getContext("webgl2")) {
      webglVersion = "webgl2";
    }

    // Get max texture size
    const gl = canvas.getContext("webgl") || canvas.getContext("webgl2");
    const maxTextureSize = gl?.getParameter(gl.MAX_TEXTURE_SIZE) ?? 2048;

    return {
      hasWebGPU,
      webglVersion,
      maxTextureSize
    };
  }

  static async createOptimalRenderer(): Promise<THREE.Renderer> {
    const capabilities = await this.detectCapabilities();

    console.log("Graphics Capabilities:", capabilities);

    if (capabilities.hasWebGPU) {
      console.log("Using WebGPU (next-gen graphics)");
      try {
        const canvas = document.createElement("canvas");
        return new THREE.WebGPURenderer({ canvas });
      } catch (error) {
        console.warn("WebGPU initialization failed, falling back to WebGL");
      }
    }

    console.log(`Using WebGL ${capabilities.webglVersion}`);
    return new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: "high-performance"
    });
  }
}

// Usage
const renderer = await GraphicsCapability.createOptimalRenderer();
```

## Deployment Strategies

### Static Hosting (Netlify, Vercel)

```bash
# Build the game
npm run build

# Deploy dist/ folder
# Netlify: drag and drop dist/ or connect Git repo
# Vercel: vercel deploy --prod
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Deploy:
```bash
docker build -t legion-game .
docker run -p 80:80 legion-game
```

### CDN Configuration (Cloudflare)

```toml
# wrangler.toml (Cloudflare Workers)
name = "legion-game"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[env.production]
routes = [
  { pattern = "legion.example.com/*", zone_name = "example.com" }
]

[build]
command = "npm run build"
cwd = "./legion-game"
```

## Version Control for Game Projects

### .gitignore for Three.js Games

```
# Build outputs
dist/
build/
*.tsbuildinfo

# Dependencies
node_modules/
package-lock.json
yarn.lock

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Large assets (use Git LFS)
*.fbx
*.blend
*.usdz
*.obj

# Save files
saves/
*.sav

# Logs
logs/
*.log
npm-debug.log*

# Environment
.env
.env.local
```

Use Git LFS for large files:
```bash
git lfs install
git lfs track "*.fbx" "*.blend" "*.usdz" "*.png" "*.jpg"
git add .gitattributes
```

### Branching Strategy

```
main (Production releases)
  ↑
  ├─← release/0.1 (Release candidate)
  │
develop (Integration branch)
  ↑
  ├─← feature/factory-system
  ├─← feature/rts-combat
  ├─← feature/procedural-generation
  ├─← bugfix/input-lag
  └─← perf/memory-optimization
```

Workflow:
1. Create feature branch from `develop`
2. Develop and test locally
3. Submit PR for code review
4. Merge to `develop` after approval
5. Weekly integration build from `develop`
6. Release branches cherry-pick fixes from `develop`
7. Merge release to `main` for shipping

## Live Patching & Hot Updates

### Version Management

```typescript
const GAME_VERSION = "0.1.0";

class VersionManager {
  async checkForUpdates(): Promise<{ updateAvailable: boolean; version: string }> {
    try {
      const response = await fetch("/api/game-version");
      const data = await response.json();

      return {
        updateAvailable: data.version !== GAME_VERSION,
        version: data.version
      };
    } catch (error) {
      console.error("Failed to check for updates:", error);
      return { updateAvailable: false, version: GAME_VERSION };
    }
  }

  async downloadUpdate(version: string): Promise<Blob> {
    const response = await fetch(`/updates/${version}/game.wasm.gz`);
    return response.blob();
  }

  async applyUpdate(blob: Blob): Promise<void> {
    // Decompress and apply update
    // For web games, typically a full rebuild is reloaded
    location.reload();
  }
}
```

### Service Worker for Offline Play

```typescript
// src/service-worker.ts
self.addEventListener("install", (event: ExtendableEvent) => {
  event.waitUntil(
    caches.open("legion-v0.1.0").then((cache) => {
      return cache.addAll([
        "/",
        "/index.html",
        "/dist/main.js",
        "/dist/three.js",
        "/config/buildings.json",
        "/assets/models/factory.glb",
        "/assets/textures/metal.png"
      ]);
    })
  );
});

self.addEventListener("fetch", (event: FetchEvent) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response;
      }

      // For online requests, fetch and cache
      return fetch(event.request).then((response) => {
        if (response.ok && event.request.method === "GET") {
          const cache = caches.open("legion-v0.1.0");
          cache.then((c) => c.put(event.request, response.clone()));
        }
        return response;
      });
    })
  );
});
```

Register the service worker:
```typescript
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js");
}
```

## Post-Launch Monitoring

### Error Tracking with Sentry

```typescript
import * as Sentry from "@sentry/browser";

Sentry.init({
  dsn: "https://your-sentry-key@sentry.io/project-id",
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  beforeSend(event) {
    // Filter out unnecessary errors
    if (event.exception) {
      const error = event.exception[0]?.value ?? "";
      if (error.includes("ResizeObserver")) {
        return null; // Ignore ResizeObserver errors
      }
    }
    return event;
  }
});

// Wrap critical code
try {
  criticalGameFunction();
} catch (error) {
  Sentry.captureException(error);
}
```

### User Feedback Collection

```typescript
class FeedbackCollector {
  showFeedbackForm(): void {
    const dialog = document.createElement("div");
    dialog.innerHTML = `
      <div style="position: fixed; bottom: 20px; right: 20px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 9999; max-width: 300px;">
        <h3>How's your experience?</h3>
        <textarea id="feedback" placeholder="Tell us what you think..." style="width: 100%; height: 80px;"></textarea>
        <button id="send-feedback" style="margin-top: 10px; padding: 8px 16px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer;">Send</button>
      </div>
    `;

    document.body.appendChild(dialog);

    document.getElementById("send-feedback")?.addEventListener("click", async () => {
      const text = (document.getElementById("feedback") as HTMLTextAreaElement).value;
      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ feedback: text, version: GAME_VERSION })
      });
      dialog.remove();
    });
  }
}
```

---

**Building and shipping games is as important as designing them. Robust testing, performance profiling, and user feedback loops ensure Legion reaches players polished and fun.**
